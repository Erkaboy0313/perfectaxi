from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Services,Order,RejectReason,DriverOrderHistory
from .serializers import ServiceSerializer,ClientOrderHistory,DriverOrderHistorySerializer,\
    ReasonSerializer,DriverWeeklyOrderHistorySerializer
from users.permissions import IsActive,IsDriver
from django.db.models import F, ExpressionWrapper, fields ,Func


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
