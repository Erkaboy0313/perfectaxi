from rest_framework import serializers
from .models import Order,Point,Services
from users.serializers import DriverInfoSeriazer

class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = ['point']

class OrderSeriazer(serializers.ModelSerializer):
    points = serializers.ListField(child = serializers.CharField(), write_only = True, required = False)
    point_set = PointSerializer(read_only = True,many=True)
    class Meta:
        model = Order
        exclude = ['ordered_time','taken_time','arived_time','started_time','complated_time','rejected_time']
    
    def save(self, **kwargs):
        if 'points' in self.validated_data:
            points = self.validated_data.pop('points')
            order = super().save(**kwargs)
            for point in points:
                Point.objects.create(order = order,point = point)
        else:
            order = super().save(**kwargs)
        return order

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = ['id','name']

class ClientOrderHistory(serializers.ModelSerializer):
    driver = DriverInfoSeriazer()
    category = serializers.CharField()
    service = serializers.ListField()
    class Meta:
        model = Order
        exclude = ["client","start_point","distance","carservice","services"]

class DriverOrderHistory(serializers.ModelSerializer):
    category = serializers.CharField()
    service = serializers.ListField()
    client_name = serializers.CharField()
    class Meta:
        model = Order
        exclude = ["driver","start_point","distance","carservice","services","client"]
