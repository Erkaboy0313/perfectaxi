from rest_framework import serializers
from .models import Order,Point,Services

class PointSerializer(serializers.ModelSerializer):

    class Meta:
        model = Point
        fields = ['point']

class OrderSeriazer(serializers.ModelSerializer):
    points = serializers.ListField(child = serializers.CharField(), write_only = True, required = False)
    point_set = PointSerializer(read_only = True,many=True)
    class Meta:
        model = Order
        fields = '__all__'
    
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
