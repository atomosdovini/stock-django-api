from variableIncome.models import *
from django.urls import reverse
from django.test import TestCase, Client
import json


class TestViews(TestCase):
    def setUp(self):
        client = Client()
        self.chart1 = client.get(reverse('chart1'))
        

    def test_chart1_GET(self):
        client = Client()
        response = client.get(reverse('chart1'))
        self.assertEquals(response.status_code, 200)
        # self.assertTemplateUsed(response, '')
