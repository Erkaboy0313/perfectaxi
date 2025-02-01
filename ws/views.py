from .async_view import lastOrderClient
from rest_framework.views import APIView
from rest_framework.response import Response
from asgiref.sync import async_to_sync
from utils.cordinates import FindRoute
from category.models import CarService

def last_order_client(user):
    return async_to_sync(lastOrderClient)(user)


class CalculatePrice(APIView):
    
    
    def post(self,request):
        data = request.data
        lat = data.get('latitude')
        long = data.get('longitude')
        start = f"{lat},{long}"
        sorted_points = sorted(data.get('points', []),key=lambda x: x['point_number'])
        points = [f"{x['latitude']},{x['longitude']}" for x in sorted_points]
        service = data.get('service', [])
        distance,time = async_to_sync(FindRoute().find_drive)(start, points)  # Assuming find_drive is async
        costs = async_to_sync(CarService.filter.calculatePrice)(distance=distance,time=time,service_list=service)  # Assuming calculatePrice is async
        return Response(costs)

