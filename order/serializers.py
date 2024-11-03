from rest_framework import serializers
from .models import Order,Point,Services,RejectReason,DriverOrderHistory
from users.serializers import DriverInfoSeriazer
from category.serializers import CarServiceSerializer

class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = ['point','point_number','point_address']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        lat,long = data['point'].split(',')
        data['latitude'] = lat.strip()
        data['longitude'] = long.strip()
        data.pop('point')
        return data

class OrderSeriazer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only = True)
    longitude = serializers.FloatField(write_only = True)
    points = PointSerializer(read_only = True,many=True)
    class Meta:
        model = Order
        exclude = ['ordered_time','taken_time','arived_time','started_time','complated_time','rejected_time']
    
class OrderCreateSeriazer(serializers.ModelSerializer):
    points = serializers.ListField(write_only = True, required = False)
    latitude = serializers.FloatField(write_only = True)
    longitude = serializers.FloatField(write_only = True)
    class Meta:
        model = Order
        exclude = ['ordered_time','taken_time','arived_time','started_time','complated_time','rejected_time']
    
    def save(self, **kwargs):

        if 'points' in self.validated_data:
            points = self.validated_data.pop('points')
            lat,long = self.validated_data.pop('latitude'),self.validated_data.pop('longitude')
            self.validated_data['start_point'] = f"{lat},{long}"
            order = super().save(**kwargs)
            point_objects = []
            for point in points:
                point['point'] = f"{point.pop('latitude')},{point.pop('longitude')}"
                point_objects.append(Point(order = order,**point))
            Point.objects.bulk_create(point_objects)
        else:
            order = super().save(**kwargs)
        return order

class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Services
        fields = "__all__"

class ClientOrderHistory(serializers.ModelSerializer):
    driver = DriverInfoSeriazer()
    services = ServiceSerializer(many =True)
    points = PointSerializer(many=True)
    carservice = CarServiceSerializer(read_only = True)
    class Meta:
        model = Order
        exclude = ["client","start_point","distance"]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['latitude'] = instance.start_point.split(',')[0]
        data['longitude'] = instance.start_point.split(',')[1]
        data['points'] = data.pop('points')
        return data

class OrderHistorySerializer(serializers.ModelSerializer):
    points = PointSerializer(read_only = True,many=True)
    carservice = CarServiceSerializer(read_only = True)
    class Meta:
        model = Order
        fields = ['id','points','contact_number','start_adress','start_point','distance','price','payment_type','status','reject_comment','carservice','reject_reason','started_time','complated_time']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['latitude'],data['longitude'] = data.pop('start_point').split(",")
        return data

class DriverOrderHistorySerializer(serializers.ModelSerializer):
    total_time = serializers.ReadOnlyField()
    total_price = serializers.FloatField()
    charge_price = serializers.FloatField()
    order = OrderHistorySerializer()
    class Meta:
        model = DriverOrderHistory
        fields = ["total_time","total_price","charge_price","order","time","status"]

class ReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = RejectReason
        fields = '__all__'

class DriverWeeklyOrderHistorySerializer(serializers.Serializer):
    order_date = serializers.DateField()
    weekday = serializers.IntegerField()
    total_earned = serializers.DecimalField(max_digits=10, decimal_places=2)

