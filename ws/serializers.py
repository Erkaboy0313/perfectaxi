from rest_framework import serializers
from category.models import CarService
from order.serializers import PointSerializer,Order
from users.models import Driver


class OrderToDriverSerializer(serializers.ModelSerializer):
    point_set = PointSerializer(read_only = True,many = True)
    class Meta:
        model = Order
        fields = ["contact_number","start_adress","start_point","price","payment_type","services","point_set"]

class CostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    service = serializers.CharField()
    cost = serializers.FloatField()

class DriverInfoSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = Driver 
        fields = ['name',"profile_image","car_model","car_name","car_number","car_color",]




