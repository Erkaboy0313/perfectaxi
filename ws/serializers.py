from rest_framework import serializers
from category.models import CarService

class CostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    service = serializers.CharField()
    cost = serializers.FloatField()
