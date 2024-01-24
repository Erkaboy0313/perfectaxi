from rest_framework import serializers
from .models import CarService,SavedLocation

class CarServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarService
        fields = '__all__'

class SavedLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedLocation
        fields = '__all__'