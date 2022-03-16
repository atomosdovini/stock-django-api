from rest_framework.serializers import ModelSerializer
from variableIncome.models import RecommendationImporterLoger, Research, Recommendation, Stock, Sector
from rest_framework import serializers 
from rest_framework_recursive.fields import RecursiveField

class SectorSerializer(ModelSerializer):

    class Meta:
        model = Sector
        fields = ('name','id')

class ResearchSerializer(ModelSerializer):

    class Meta:
        model = Research
        fields = ('name', 'active')

class RecommendationEditSerializer(ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ('datefinal', 'rating', 'target')

class StocksSerializer(ModelSerializer):
    sectorname = serializers.CharField(source='sector.name')
    sectorid = serializers.IntegerField(source='sector.id')

    class Meta:
        model = Stock
        fields = ('name', 'ticket', 'sectorname', 'sectorid')

class StockListSerializer(ModelSerializer):
    actual_price = serializers.FloatField(source='get_price')
    growth30d = serializers.CharField(source='get_variation_30_days')
    growth6m = serializers.CharField(source='get_variation_6_months')
    growth1y = serializers.CharField(source='get_variation_1_year')

    class Meta:
        model = Stock
        fields = ('actual_price', 'growth30d', 'growth6m', 'growth1y')

class StockSerializer(ModelSerializer):
    sectorname = serializers.CharField(source='sector.name')
    actual_price = serializers.FloatField(source='get_price')
    growth30d = serializers.CharField(source='get_variation_30_days')
    growth6m = serializers.CharField(source='get_variation_6_months')
    growth1y = serializers.CharField(source='get_variation_1_year')

    class Meta:
        model = Stock
        fields = ('name', 'ticket', 'sectorname', 'actual_price', 'growth30d', 'growth6m', 'growth1y')

class RecommendationSerializer(ModelSerializer):
    stockname = serializers.CharField(source='stock.name')
    stockticket = serializers.CharField(source='stock.ticket')
    researchname = serializers.CharField(source='research.name')
    sectorname = serializers.CharField(source='stock.sector.name')

    class Meta:
        model = Recommendation
        fields = ('id', 'initial_price', 'stockname', 'researchname', 'sectorname', 'research', 'stockticket', 'datefinal', 'rating', 'target')

class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class StockS(ModelSerializer):
    class Meta:
        model = Stock
        fields = ('name',)

class RecommendationS(ModelSerializer):
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = ('stock', 'research',)        

    def get_stock(self, obj):
        if obj.stock is not None:
            return StockS(obj.stock).data
        else:
            return None

class RecommendationImporterLogerSerializer(ModelSerializer):
    username = serializers.CharField(source="user.first_name")

    class Meta:
        model = RecommendationImporterLoger
        fields = ('username','text','status','createdat')
