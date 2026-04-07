from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from .models import CarService, SavedLocation, CarBrend, Color, CarModel


class CarServiceSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CarService)

    class Meta:
        model = CarService
        fields = '__all__'


class CarBrendSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CarBrend)

    class Meta:
        model = CarBrend
        fields = '__all__'


class ColorSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Color)

    class Meta:
        model = Color
        fields = '__all__'


class CarModelSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=CarModel)

    class Meta:
        model = CarModel
        fields = '__all__'


class SavedLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedLocation
        fields = '__all__'
