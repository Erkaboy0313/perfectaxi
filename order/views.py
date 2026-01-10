from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Services,Order,RejectReason,DriverOrderHistory,Point
from .serializers import ServiceSerializer,ClientOrderHistory,DriverOrderHistorySerializer,\
    ReasonSerializer,DriverWeeklyOrderHistorySerializer
from users.permissions import IsActive,IsDriver
from django.db.models import F, ExpressionWrapper, fields ,Func,OuterRef,Subquery
from drf_spectacular.utils import extend_schema, extend_schema_view

@extend_schema_view(
    list=extend_schema(
        summary="List all services",
        description="Returns a list of all available services.",
        responses={200: ServiceSerializer(many=True)}
    )
)
class ServicesView(viewsets.ViewSet):

    def list(self,request):
        services = Services.objects.all()
        serializer = ServiceSerializer(services,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class TimeDiffInSeconds(Func):
    function = 'EXTRACT'
    template = '%(function)s(MINUTE FROM %(expressions)s)'
 

@extend_schema(
    summary="Driver order history",
    description="Get completed orders for logged-in driver with total time and price calculations.",
    responses={200: DriverOrderHistorySerializer(many=True)},
    tags=['Orders']
)
class DriverOrderHistoryViewSet(viewsets.ViewSet):
    """
    Returns the completed order history for the logged-in driver, including time and price calculations.
    """
    permission_classes = (IsActive, IsDriver)

    def list(self, request):
        driver_orders = DriverOrderHistory.objects.select_related('order').annotate(
            total_time=ExpressionWrapper(
                TimeDiffInSeconds(F('order__complated_time') - F('order__started_time')),
                output_field=fields.IntegerField()
            ),
            charge_price=F('order__charge__charged_fund'),
            total_price=ExpressionWrapper(
                F('order__price') - F('charge_price'),
                output_field=fields.FloatField()
            )
        )
        serializer = DriverOrderHistorySerializer(driver_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Client order history",
    description="Get all orders of the logged-in client including driver and service info.",
    responses={200: ClientOrderHistory(many=True)},
    tags=['Orders']
)
class ClientOrderHistoryViewSet(viewsets.ViewSet):
    """
    Returns the order history for the logged-in client, including related driver and service info.
    """
    permission_classes = (IsActive,)

    def list(self, request):
        orders = Order.objects.filter(client__user=request.user).prefetch_related('driver', 'carservice')
        serializer = ClientOrderHistory(orders, many=True)
        return Response(serializer.data, status=200)


@extend_schema_view(
    list=extend_schema(
        summary="List reject reasons",
        description="Returns all possible reasons for rejecting an order.",
        responses={200: ReasonSerializer(many=True)}
    )
)  
class RejectReasonView(viewsets.ViewSet):
    permission_classes = (IsActive,)
    
    def list(self,request):
        resons = RejectReason.objects.all()
        serializer = ReasonSerializer(resons,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)





@extend_schema_view(
    list=extend_schema(
        summary="Driver weekly report",
        description=(
            "Returns a summary of the driver’s completed orders for the last 7 days. "
            "Only accessible to users with driver role."
        ),
        responses={200: DriverWeeklyOrderHistorySerializer(many=True)}
    )
)
class DriverWeeklyReportView(viewsets.ViewSet):
    permission_classes = (IsActive,IsDriver)
    
    def list(self,request):
        data = DriverOrderHistory.report.get_last_7_days_report(request.user)
        serializer = DriverWeeklyOrderHistorySerializer(data,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)

@extend_schema_view(
    list=extend_schema(
        summary="Get last 5 destinations",
        description=(
            "Fetches the last 5 destinations (latitude, longitude, address) "
            "of the logged-in client based on their recent orders."
        ),
        responses={
            200: {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'order_id': {'type': 'integer', 'example': 123},
                        'latitude': {'type': 'number', 'example': 41.311081},
                        'longitude': {'type': 'number', 'example': 69.240562},
                        'destination_address': {'type': 'string', 'example': 'Tashkent, Uzbekistan'}
                    }
                }
            }
        }
    )
)
class LastDestinationsViewSet(viewsets.ViewSet):
    """
    A ViewSet to fetch the last 5 destinations (point and address) of a logged-in client.
    """
    permission_classes = [IsActive]

    def list(self, request, *args, **kwargs):
        orders = Order.objects.filter(client__user=request.user)

        latest_points = Point.objects.filter(order=OuterRef('pk')).order_by('-point_number')
        orders = orders.annotate(
            last_point_number=Subquery(latest_points.values('point_number')[:1]),
            last_point_address=Subquery(latest_points.values('point_address')[:1]),
            last_point=Subquery(latest_points.values('point')[:1])
        )

        orders_with_destinations = orders.exclude(last_point_number__isnull=True).order_by('-id')[:5]

        data = [
            {
                "order_id": order.id,
                "latitude":float(order.last_point.split(',')[0]),
                "longitude":float(order.last_point.split(',')[1]),
                "destination_address": order.last_point_address
            }
            for order in orders_with_destinations
        ]
        
        return Response(data)
