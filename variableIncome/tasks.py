from __future__ import absolute_import, unicode_literals

from celery import shared_task
from variableIncome.serializers import *
from variableIncome.models import Research, Recommendation, Sector, Stock, RecommendationImporterLoger, get_stock
from variableIncome.views import *
import pandas as pd
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()
@shared_task
def add(x, y):
    return x + y

def add_stock(ticket, sector, name):
    print(check_yahoo_available(ticket))
    if check_yahoo_available(ticket) == True:
        stock_obj = Stock.objects.create(sector=sector, ticket=str(ticket), name=str(name), is_yahoo_available=True)
        stock_obj.save()
        return stock_obj
    else:
        return False

@shared_task
def add_massive_recomendations_task(df):
    counter = 0
    df = pd.DataFrame.from_dict(df)
    print(df)
    for index, row in df.iterrows():
        setor = ""
        stock = False
        research = ""
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
            stock = add_stock(row["ticker"], setor, row['acao'])
            if stock == False:
                success = success + "Erro linha " + str(counter) + ": Ação " + str(row["acao"]) + " não encontrada.<br>"     
        try:
            research = Research.objects.get(name=row["research"])
        except:
            success = success + "Erro linha " + str(counter) + ": Research " + str(row["research"]) + " não encontrada.<br>" 
        # try:
            
        date_final_obj = datetime.strptime(row["fechamento"], '%d/%m/%Y')
        
        datefinal = date_final_obj.strftime('%Y-%m-%d')
        # except:
        #     success = success + "Erro linha " + str(counter) + ": Data incorreta.<br>"     
        
        try:
            r = Recommendation.objects.filter(research=research, stock=stock, datefinal=datefinal, rating=row["rating"], target=row['preco_alvo'])
        except:
            success = success + "Não Salvo<br>" 
        if row["preco_alvo"] != None and str(row["preco_alvo"]) != "nan":    
            target = row["preco_alvo"]
        else:
            success = success + "Erro linha " + str(counter) + ": Target Inválido"
        if success == "":
            if r.exists() == False and r!=0:
                print('---------------------------------------------------------------')
                print('------------date_initial_obj', date_final_obj.strftime('%d-%m-%Y'))

                initial_price = stock.get_price_on_date(date_final_obj.strftime('%d-%m-%Y'))
                r = Recommendation.objects.create(initial_price=initial_price, research=research,stock=stock,datefinal=datefinal, rating=row["rating"], target=target)
                print(r)
                r.save()
            else:
                success = success + "Erro linha " + str(counter) + ": Já há uma recomendação desta na base de dados."
        if success == "":
            success = f"Linha {counter} finalizada com sucesso. {r.id} {stock} a um preço alvo de {target}"
        else:
            success = success 
        print('-----sucess', success)
        user = User.objects.first()
        # user = request.user
        obj = RecommendationImporterLoger.objects.create(user=user, text=success)
        obj.save()    
    return True