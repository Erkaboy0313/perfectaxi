from rest_framework import serializers
from order.serializers import PointSerializer,Order
from users.models import Driver
from order.serializers import OrderSeriazer


class OrderToDriverSerializer(serializers.ModelSerializer):
    point_set = PointSerializer(read_only = True,many = True)
    class Meta:
        model = Order
        fields = ["contact_number","start_adress","start_point","price","payment_type","services","point_set"]

class CostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    service = serializers.CharField()
    cost = serializers.FloatField()

    def to_representation(self, instance):
        obj = super().to_representation(instance)
        def roundPrice(price):
            rounded_hundreds = int(price / 100) % 10  # Extract the hundreds part and round it
            if rounded_hundreds >= 7:
                rounded_price = int(price / 1000) * 1000 + 1000
            elif rounded_hundreds >= 3:
                rounded_price = int(price / 1000) * 1000 + 500
            else:
                rounded_price = int(price / 1000) * 1000
            return rounded_price
        obj['cost'] = roundPrice(obj['cost'])
        return obj

class DriverInfoSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()

    class Meta:
        model = Driver 
        fields = ['id','name',"profile_image","car_model","car_name","car_number","car_color",]

class LastOrderSerializer(OrderSeriazer):
    driver = DriverInfoSerializer()
