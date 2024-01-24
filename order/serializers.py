from rest_framework import serializers
from .models import Order,Point,Services,RejectReason,DriverOrderHistory
from users.serializers import DriverInfoSeriazer

class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = ['point','point_number','point_address']

class OrderSeriazer(serializers.ModelSerializer):
    points = serializers.ListField(child = PointSerializer(), write_only = True, required = False)
    point_set = PointSerializer(read_only = True,many=True)
    class Meta:
        model = Order
        exclude = ['ordered_time','taken_time','arived_time','started_time','complated_time','rejected_time']
    
    def save(self, **kwargs):
        if 'points' in self.validated_data:
            points = self.validated_data.pop('points')
            order = super().save(**kwargs)
            for point in points:
                Point.objects.create(order = order,**point)
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

class OrderHistorySerializer(serializers.ModelSerializer):
    point_set = PointSerializer(read_only = True,many=True)
    class Meta:
        model = Order
        fields = ['id','point_set','contact_number','start_adress','start_point','distance','price','payment_type','status','reject_comment','carservice','reject_reason','started_time','complated_time']

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

