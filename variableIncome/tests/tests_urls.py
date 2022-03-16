from django.test import SimpleTestCase
from django.urls import reverse, resolve
from variableIncome.views import *

class TestUrls(SimpleTestCase):

    def test_chart1_url_is_resolved(self):
        url = reverse('chart1')
        self.assertEquals(resolve(url).func.view_class, ChartResearchs)

    def test_chart2_url_is_resolved(self):
        url = reverse('chart2')
        self.assertEquals(resolve(url).func.view_class, ChartResearchsMedia)

    def test_stocks_url_is_resolved(self):
        url = reverse('stocks')
        self.assertEquals(resolve(url).func.view_class, StockAPIView)

    def test_stockslist_url_is_resolved(self):
        url = reverse('stockslist')
        self.assertEquals(resolve(url).func.view_class, StockListAPIView)

    def test_recommendations_url_is_resolved(self):
        url = reverse('recommendations')
        self.assertEquals(resolve(url).func.view_class, RecommendationAPIListView)

    def test_recommendationcsv_url_is_resolved(self):
        url = reverse('recommendationcsv')
        self.assertEquals(resolve(url).func.view_class, RecommendationCSVAPIView)

    def test_sectors_url_is_resolved(self):
        url = reverse('sectors')
        self.assertEquals(resolve(url).func.view_class, SectorAPIListView)

    def test_researchs_url_is_resolved(self):
        url = reverse('researchs')
        self.assertEquals(resolve(url).func.view_class, ResearchAPIListView)

    def test_csrfcookie_url_is_resolved(self):
        url = reverse('csrfcookie')
        self.assertEquals(resolve(url).func.view_class, GetCSRFToken)
