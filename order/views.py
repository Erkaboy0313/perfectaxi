from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Services,Order,RejectReason,DriverOrderHistory,Point
from .serializers import ServiceSerializer,ClientOrderHistory,DriverOrderHistorySerializer,\
    ReasonSerializer,DriverWeeklyOrderHistorySerializer
from users.permissions import IsActive,IsDriver
from django.db.models import F, ExpressionWrapper, fields ,Func,OuterRef,Subquery


class ServicesView(viewsets.ViewSet):

    def list(self,request):
        services = Services.objects.all()
        serializer = ServiceSerializer(services,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class OrderHistoryView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def list(self,request):
        if request.user.role == "driver":
            
            class TimeDiffInSeconds(Func):
                function = 'EXTRACT'
                template = '%(function)s(MINUTE FROM %(expressions)s)'
                
            driver_orders = DriverOrderHistory.objects.select_related('order').\
                annotate(
                    total_time = ExpressionWrapper(
                        TimeDiffInSeconds(F('order__complated_time') - F('order__started_time')),
                        output_field=fields.IntegerField()
                    ),
                    charge_price=F('order__charge__charged_fund'),
                    total_price=ExpressionWrapper(
                        F('order__price') - F('charge_price'),
                        output_field=fields.FloatField()
                    )
                )
            serializer = DriverOrderHistorySerializer(driver_orders,many = True)
        if request.user.role == "client":
            
            orders = Order.objects.filter(client__user = request.user).prefetch_related('driver','carservice')
            serializer = ClientOrderHistory(orders,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class RejectReasonView(viewsets.ViewSet):
    permission_classes = (IsActive,)
    
    def list(self,request):
        resons = RejectReason.objects.all()
        serializer = ReasonSerializer(resons,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class DriverWeeklyReportView(viewsets.ViewSet):
    permission_classes = (IsActive,IsDriver)
    
    def list(self,request):
        data = DriverOrderHistory.report.get_last_7_days_report(request.user)
        serializer = DriverWeeklyOrderHistorySerializer(data,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)


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
