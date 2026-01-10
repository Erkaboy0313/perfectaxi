from .async_view import lastOrderClient
from rest_framework.views import APIView
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from utils.cordinates import FindRoute
from category.models import CarService
from drf_spectacular.utils import extend_schema
def last_order_client(user):
    return async_to_sync(lastOrderClient)(user)

from rest_framework import serializers








class CalculatePricePointSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    point_number = serializers.IntegerField()


class CalculatePriceRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    points = CalculatePricePointSerializer(many=True)
    service = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class CalculatePriceResponseSerializer(serializers.Serializer):
    distance = serializers.FloatField()
    time = serializers.IntegerField()
    costs = serializers.DictField()




@extend_schema(
    summary="Calculate ride price",
    description=(
        "Calculates the total ride price based on start coordinates, "
        "intermediate points, and selected services."
    ),
    request=CalculatePriceRequestSerializer,
    responses={200: CalculatePriceResponseSerializer},
    tags=['Orders']
)
class CalculatePrice(APIView):

    def post(self, request):
        serializer = CalculatePriceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        lat = data['latitude']
        lng = data['longitude']
        start = f"{lat},{lng}"

        sorted_points = sorted(
            data.get('points', []),
            key=lambda x: x['point_number']
        )

        points = [f"{p['latitude']},{p['longitude']}" for p in sorted_points]
        service = data.get('service', [])

        distance, time = async_to_sync(FindRoute().find_drive)(start, points)
        costs = async_to_sync(CarService.filter.calculatePrice)(
            distance=distance,
            time=time,
            service_list=service
        )

        return Response( costs )
