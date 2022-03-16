from enum import unique
from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from pandas_datareader import data as web
import pandas as pd
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from decouple import config

base = config("API_ADDRESS")
User = get_user_model()

def get_stock(ticket, start='i', end='i'):
    try:
        if start == 'i' or end == 'i':
            hj = datetime.now()
            end = datetime(hj.year,hj.month,hj.day)
            d = relativedelta(days=6)
            start = end - d
        return web.DataReader(f'{ticket}.SA', data_source='yahoo', start=start, end=end)
    except:
        return 0.00


def check_yahoo_available(ticket):
    hj = datetime.now()
    end = datetime(hj.year,hj.month,hj.day)
    d = relativedelta(days=6)
    start = end - d
    try:
        web.DataReader(f'{ticket}.SA', data_source='yahoo', start=start, end=end)
    except:
        return False    
    else:
        return True

def get_growth(ticket, months):
    n = datetime.now()
    d = relativedelta(months=months)
    n = n - d
    d = relativedelta(days=8)
    n1 = n - d
    try:
        c_i = get_stock(ticket, n1, n)
        c_f = get_stock(ticket)
        first_price = c_i.iat[0,5]
        last_price = c_f.iat[0,5]
        return round((float(last_price)-float(first_price))*100/float(first_price), 2)
    except:
        return 0.00

class Research(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    createdat = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = 'Researchs'

class Sector(models.Model):
    name = models.CharField(max_length=255, unique=True)
    createdat = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = 'Sectors'        

class Stock(models.Model):
    name = models.CharField(max_length=255)
    ticket = models.CharField(max_length=6, unique=True)
    sector = models.ForeignKey(Sector, models.DO_NOTHING, verbose_name='Setor')
    is_yahoo_available = models.BooleanField(default=False)
    createdat = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)  

    def get_price(self):  
        try:
            return round(get_stock(self.ticket).iat[-1,5],2)
        except:
            return 0.00

    def get_price_on_date(self, date): 
        try:
            c = get_stock(self.ticket, date, date)
            return round(c.iat[0,5],2)
        except:
            return 0.00        

    def get_price_period_df(self, start, end):
        try:
            c = get_stock(self.ticket, start, end)
            # cria coluna com datas
            c = c.assign(Date = c.index.values)
            return pd.DataFrame(data=c,columns=['Date', 'Close'])
        except:
            return 0.00

    def get_price_period(self, start, end): 
        try:
            c = get_stock(self.ticket, start, end)
            # cria coluna com datas
            c = c.assign(Date = c.index.values)
            return pd.DataFrame(data=c,columns=['Date', 'Close']).to_numpy()
        except:
            return 0.00

    def get_variation_30_days(self):
        try:
            return get_growth(self.ticket, 1)
        except:
            return 0.00

    def get_variation_6_months(self):
        try:
            return get_growth(self.ticket, 6)
        except:
            return 0.00

    def get_variation_1_year(self):
        try:
            return get_growth(self.ticket, 12)
        except:
            return 0.00        

    # def get_all(self):
    #     n = datetime.now()
    #     d = relativedelta(months=12)
    #     n = n - d
    #     df = get_stock(self.ticket, start=n.strftime('%d-%m-%Y'), end=datetime.now().strftime('%d-%m-%Y'))
        

    def __str__(self):
        return str(self.name)

    class Meta:
        managed = True
        db_table = 'Stocks'     

CHOICES = (
    ('COMPRA', 'COMPRA'),
    ('VENDA', 'VENDA'),
    ('NEUTRO', 'NEUTRO'),
    ('REVISAO', "SOB REVISÃO"),
)

class Recommendation(models.Model):
    research = models.ForeignKey(Research, models.DO_NOTHING, verbose_name='Fonte')
    stock = models.ForeignKey(Stock, models.DO_NOTHING, verbose_name='Ação', related_name='recommendations')
    # date = models.DateField()
    datefinal = models.DateField()
    rating = models.CharField(choices=CHOICES, max_length=30, verbose_name='Rating')
    target = models.FloatField(verbose_name='Preço Alvo', default=0.00)
    status = models.BooleanField(default=True)
    initial_price = models.FloatField(verbose_name='Cotação dia da recomendação', default=0.00)
    createdat = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)  
    
    def __str__(self):
        return str(self.stock) + " - " + str(self.research)

    class Meta:
        managed = True
        db_table = 'Recommendations'
        ordering = ('-datefinal',)           


class RecommendationImporterLoger(models.Model):
    createdat = models.DateTimeField(db_column='createdAt', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='updatedAt', auto_now=True)  
    status = models.BooleanField()
    text = models.TextField()
    user = models.ForeignKey(User, models.DO_NOTHING, verbose_name='Usuário')

    class Meta:
        managed = True
        ordering = ('-updatedat',)    

    def __str__(self):
        return str(self.text)