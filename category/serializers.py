from rest_framework import serializers
from .models import CarService,SavedLocation,CarBrend,Color

class CarServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarService
        fields = '__all__'

class SavedLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedLocation
        fields = '__all__'

class CarBrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrend
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


