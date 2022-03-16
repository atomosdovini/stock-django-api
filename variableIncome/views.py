from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.views import APIView
from variableIncome.serializers import *
from variableIncome.models import CHOICES as rating_choices
from variableIncome.models import Research, Recommendation, Sector, Stock, RecommendationImporterLoger, check_yahoo_available, get_growth, get_stock
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.http import require_POST
from .paginations import NewPagination
import pandas as pd
import io
from variableIncome.tasks import add_massive_recomendations_task
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Case, Value, When, Count
from asgiref.sync import sync_to_async
import after_response
from django.core.signals import request_finished
from django.dispatch import receiver
from .utils import get_last_year_date
import json
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated



User = get_user_model()

@after_response.enable
def add_massive_reccomendations(request, df):
    counter = 0
    for index, row in df.iterrows():
        setor = ""
        stock = False
        research = ""
        rating = ""
        target = ""
        date_initial_obj = ""
        date_final_obj = ""
        dateinitial = ""
        datefinal = ""
        initial_price = ""
        r = 0
        counter += 1
        success = ''
        try:
            setor = Sector.objects.get(name=row["setor"])
        except:
            success = "Erro linha " + str(counter) + ": Setor " + str(row["setor"]) + " não encontrado.<br>"    
        try:
            stock = Stock.objects.get(ticket=row["ticker"])
        except:
            if success == "":
                stock = add_stock(row["ticker"], setor, row['acao'])
                if stock == False:
                    success = success + "Erro linha " + str(counter) + ": Ação " + str(row["acao"]) + " não encontrada.<br>"     
        try:
            research = Research.objects.get(name=row["research"])
        except:
            success = success + "Erro linha " + str(counter) + ": Research " + str(row["research"]) + " não encontrada.<br>" 
        try:
            rating = str(row["rating"]).upper()
            if not rating in str(rating_choices):
                success = success + "Erro linha " + str(counter) + ": Rating fora do padrão.<br>" 
        except:
            success = success + "Erro linha " + str(counter) + ": Rating fora do padrão.<br>" 
        # try:
        date_final_obj = datetime.strptime(row["fechamento"], '%d/%m/%Y')
        datefinal = date_final_obj.strftime('%Y-%m-%d')
        # except:
        #     success = success + "Erro linha " + str(counter) + ": Data incorreta.<br>"     
        try:
            r = Recommendation.objects.filter(research=research, stock=stock, datefinal=datefinal, rating=rating, target=row['preco_alvo'])
        except:
            success = success + "Não Salvo<br>" 
        if row["preco_alvo"] != None and str(row["preco_alvo"]) != "nan":    
            target = row["preco_alvo"]
        else:
            success = success + "Erro linha " + str(counter) + ": Target Inválido"
        if success == "":
            if r.exists() == False and r!=0:
                initial_price = stock.get_price_on_date(date_final_obj.strftime('%d-%m-%Y'))
                r = Recommendation.objects.create(initial_price=initial_price, research=research,stock=stock, datefinal=datefinal, rating=rating, target=target)
                print(r)
                r.save()
            else:
                success = success + "Erro linha " + str(counter) + ": Já há uma recomendação desta na base de dados."
        if success == "":
            status = True
            success = f"Linha {counter} finalizada com sucesso. {r.id} {stock} a um preço alvo de {target}"
        else:
            status = False
            success = success 
        # user = User.objects.first()
        user = request.user
        obj = RecommendationImporterLoger.objects.create(user=user, text=success, status=status)
        obj.save()


def add_stock(ticket, sector, name):
    if check_yahoo_available(ticket) == True:
        stock_obj = Stock.objects.create(sector=sector, ticket=str(ticket), name=str(name), is_yahoo_available=True)
        stock_obj.save()
        return stock_obj
    else:
        return False


class StockListAPIView(APIView):   
    def get(self, request, format=None):
        try:
            ticket = request.GET.get('ticket')
            item = Stock.objects.get(ticket=ticket)
            serializer = StockListSerializer(item)
            return Response(serializer.data)
        except Stock.DoesNotExist:
            return Response(status=404)
    
class ChartResearchs(APIView):
    def get(self, request, format=None):
        try:
            ticket = request.GET.get('ticket')
        except:
            return Response(status=404)
        stock = Stock.objects.get(ticket=ticket)
        last_year_date = get_last_year_date()
        recommendations = Recommendation.objects.filter(stock=stock).distinct('datefinal', 'research', 'stock')
        valores = stock.get_price_period_df(last_year_date, datetime.now().strftime('%d-%m-%Y'))
        researchs = recommendations.values('research__name').distinct().order_by()
        recommendations = recommendations.values('research__name', 'datefinal', 'target')
        res = ['Date', 'Close',]
        for r in researchs:
            res.append(r['research__name'])
        df = pd.DataFrame(valores, columns=res)
        date = 0
        for index, row in df.iterrows():
            for r in recommendations:
                if row['Date'] == r['datefinal']:
                    df.at[row['Date'], r['research__name']] = r['target']
                else:
                    if date == 0:
                        df.at[row['Date'], r['research__name']] = 0
                    else:
                        df.at[row['Date'], r['research__name']] = df.at[date, r['research__name']]
            date = row['Date']
        # pd.set_option("display.max_rows", None, "display.max_columns", None)
        # print(df)
        df = df.astype({ "Date": str }).round(2)
        result = df.to_json(orient='records')
        return JsonResponse(json.loads(result), safe = False)

class ChartResearchsMedia(APIView):
    def get(self, request, format=None):
        try:
            ticket = request.GET.get('ticket')
        except:
            return Response(status=404)
        stock = Stock.objects.get(ticket=ticket)
        last_year_date = get_last_year_date()
        recommendations = Recommendation.objects.filter(stock=stock).distinct('datefinal', 'research', 'stock')
        valores = stock.get_price_period_df(last_year_date, datetime.now().strftime('%d-%m-%Y'))
        researchs = recommendations.values('research__name').distinct().order_by()
        recommendations = recommendations.values('research__name',  'datefinal', 'target')
        res = ['Date', 'Close', 'Media']
        for r in researchs:
            res.append(r['research__name'])
        date = 0
        df = pd.DataFrame(valores, columns=res)
        for index, row in df.iterrows():
            n = 0
            som = 0
            for r in recommendations:
                if row['Date'] == r['datefinal']:
                    df.at[row['Date'], r['research__name']] = r['target']
                else:
                    if date == 0:
                        df.at[row['Date'], r['research__name']] = 0
                    else:
                        df.at[row['Date'], r['research__name']] = df.at[date, r['research__name']]

            for research in researchs:
                v = df.at[row['Date'], research['research__name']]
                if v != 0:
                    n = n + 1
                    som = som + v
            if n != 0:
                df.at[row['Date'], 'Media'] = som/n
            df.at[row['Date'], 'Date'] = row['Date'].strftime('%d-%m-%Y')
            date = row['Date']

        for r in researchs:
            df.pop(r['research__name'])
        df = df.astype({ "Date": str }).round(2)

        result = df.to_json(orient='records')
        return JsonResponse(json.loads(result), safe = False)

class StockAPIView(APIView):   
    def delete(self, request, format=None):
        try:
            item = Stock.objects.get(ticket=request.data['ticket'])
        except Stock.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

    def get(self, request, format=None):
        ticket = request.GET.get('ticket')
        if ticket:
            try:
                item = Stock.objects.get(ticket=ticket)
                serializer = StockSerializer(item)
                return Response(serializer.data)
            except Stock.DoesNotExist:
                return Response(status=404)

        sector_list_query = request.GET.getlist('sector[]')
        s_q = Q()
        q = Q()

        if sector_list_query:
            for f in sector_list_query:
                s_q.connector = Q.OR
                s_q.add(Q(sector__id=int(f)), Q.OR)
                q = q & s_q
        if not sector_list_query:
            items = Stock.objects.order_by('pk')
        else:
            items = Stock.objects.filter(q)            
        items = items.order_by('ticket')
        paginator = NewPagination()
        paginator.page_size = 5
        result_page = paginator.paginate_queryset(items, request)
        serializer = StocksSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class RecommendationCSVAPIView(APIView):
    def post(self, request, format=None):
        df = pd.read_csv(io.StringIO(request.FILES['recommendations'].read().decode('latin1')), delimiter=';')
        # add_massive_recomendations_task(df.to_dict())
        add_massive_reccomendations.after_response(request, df)
        return Response({ 'success': True })

class CheckAuthenticatedView(APIView):
    def get(self, request, format=None):
        user = self.request.user
        try:
            isAuthenticated = user.is_authenticated

            if isAuthenticated:
                return Response({ 'isAuthenticated': 'success' })
            else:
                return Response({ 'isAuthenticated': 'error' })
        except:
            return Response({ 'error': 'Something went wrong when checking authentication status' })

class ResearchAPIView(APIView):
    @csrf_exempt
    def get(self, request, id, format=None):
        try:
            item = Research.objects.get(pk=id)
            serializer = ResearchSerializer(item)
            return Response(serializer.data)
        except Research.DoesNotExist:
            return Response(status=404)
    
    @csrf_exempt
    def put(self, request, id, format=None):
        try:
            item = Research.objects.get(pk=id)
        except Research.DoesNotExist:
            return Response(status=404)
        serializer = ResearchSerializer(item, data=request.data.get('researchFormData'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @csrf_exempt
    def delete(self, request, id, format=None):
        try:
            item = Research.objects.get(pk=id)
        except Research.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)

class SectorAPIListView(APIView):
    def get(self, request, format=None):
        items = Sector.objects.order_by('pk')
        serializer = SectorSerializer(items, many=True)
        return Response(serializer.data)

class ResearchAPIListView(APIView):
    def get(self, request, format=None):
        items = Research.objects.order_by('pk')
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(items, request)
        serializer = ResearchSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = ResearchSerializer(data=request.data.get('researchFormData'))
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data, status=201)
            return response
        return Response(serializer.errors, status=400)

class RecommendationAPIView(APIView):
    def get(self, request, id, format=None):
        try:
            item = Recommendation.objects.get(pk=id)
            serializer = RecommendationSerializer(item)
            return Response(serializer.data)
        except Recommendation.DoesNotExist:
            return Response(status=404)
    
    def put(self, request, id, format=None):
        try:
            item = Recommendation.objects.get(pk=id)
        except Recommendation.DoesNotExist:
            return Response(status=404)
        serializer = RecommendationEditSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    @csrf_exempt
    def delete(self, request, id, format=None):
        try:
            item = Recommendation.objects.get(pk=id)
        except Recommendation.DoesNotExist:
            return Response(status=404)
        item.delete()
        return Response(status=204)


class RecommendationAPIListView(APIView):
    @csrf_exempt
    def get(self, request, format=None):
        research_query = request.GET.get('research')
        research_list_query = request.GET.getlist('research[]')
        sector_query = request.GET.get('sector')
        sector_list_query = request.GET.getlist('sector[]')
        rating_query = request.GET.get('rating')
        rating_list_query = request.GET.getlist('rating[]')
        date_i_query = request.GET.get('date_i')
        date_f_query = request.GET.get('date_f')
        ticket_query = request.GET.get('ticket')
        q = Q()
        r_q = Q()
        s_q = Q()
        ra_q = Q()

        if research_list_query:
            for f in research_list_query:
                r_q.connector = Q.OR
                
                r_q.add(Q(research__name=str(f)), Q.OR)
                q = q & r_q
      
        if sector_list_query:
            for f in sector_list_query:
                s_q.connector = Q.OR
                s_q.add(Q(stock__sector__id=int(f)), Q.OR)
                q = q & s_q

        if rating_list_query:
            for f in rating_list_query:
                ra_q.connector = Q.OR
                ra_q.add(Q(rating=str(f).upper()), Q.OR)
                q = q & ra_q

        if ticket_query:
            t_q = Q()
            t_q.connector = Q.OR
            t_q = t_q.add(Q(stock__ticket=str(ticket_query)), Q.OR)
            q = q & t_q

        if not research_query and not research_list_query and not sector_query and not sector_list_query and not rating_query and not rating_list_query and not date_f_query and not date_i_query:
            items = Recommendation.objects.order_by('pk')
        else:
            items = Recommendation.objects.none()     

        if date_i_query and date_f_query:
            d_q = Q(datefinal__range=[date_i_query,date_f_query])
            q = q & d_q

        if q == Q():
            n =  datetime.now() - relativedelta(months=1)
            q = Q(datefinal__range=[n.strftime('%Y-%m-%d'),datetime.now().strftime('%Y-%m-%d')])

        items = Recommendation.objects.filter(q).order_by("stock")
        paginator = NewPagination()
        paginator.page_size = 25

        result_page = paginator.paginate_queryset(items, request)
        serializer = RecommendationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = RecommendationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data, status=201)
            return response
        return Response(serializer.errors, status=400)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):

    permission_classes = (permissions.AllowAny,)
    def get(self, request, format=None):
        response = Response({'success': 'verdade'})
        return response


class RecommendationImporterLogerAPIListView(APIView):
    def get(self, request, format=None):
        items = RecommendationImporterLoger.objects.all()
        paginator = NewPagination()
        paginator.page_size = 55
        result_page = paginator.paginate_queryset(items, request)
        serializer = RecommendationImporterLogerSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)        