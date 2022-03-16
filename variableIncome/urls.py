from django.conf.urls import include, url
from variableIncome import views

from django.urls import path


urlpatterns = [
#   Log importador
  path('log/', views.RecommendationImporterLogerAPIListView.as_view()),
  
        # charts
  path('chart-1/', views.ChartResearchs.as_view(), name='chart1'),
  path('chart-2/', views.ChartResearchsMedia.as_view(), name='chart2'),
         # ações
  path('stocks/', views.StockAPIView.as_view(), name='stocks'),
  path('stocks-list/', views.StockListAPIView.as_view(), name='stockslist'),
         # recomendações
  url(r'^recommendation/(?P<id>[0-9]+)/$', views.RecommendationAPIView.as_view(), name='recommendation'),
  path('recommendation/', views.RecommendationAPIListView.as_view(), name='recommendations'),
  path('recommendation-file/', views.RecommendationCSVAPIView.as_view(), name='recommendationcsv'),
        # setores
  path('sectors/', views.SectorAPIListView.as_view(), name='sectors'),
            # fonte de recomendacoes
  url(r'^research/(?P<id>[0-9]+)/$', views.ResearchAPIView.as_view(), name='research'),
  path('research/', views.ResearchAPIListView.as_view(), name='researchs'),
         # cookie
  path('csrf_cookie/', views.GetCSRFToken.as_view(), name='csrfcookie'),
]