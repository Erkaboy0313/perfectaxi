from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Services,Order
from .serializers import ServiceSerializer,ClientOrderHistory,DriverOrderHistory
from users.permissions import IsActive

class ServicesView(viewsets.ViewSet):

    def list(self,request):
        services = Services.objects.all()
        serializer = ServiceSerializer(services,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class OrderHistoryView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def list(self,request):
        if request.user.role == "driver":
            orders = Order.objects.filter(driver__user = request.user).prefetch_related('client','carservice')
            serializer = DriverOrderHistory(orders,many = True)
        if request.user.role == "client":
            orders = Order.objects.filter(client__user = request.user).prefetch_related('driver','carservice')
            serializer = ClientOrderHistory(orders,many = True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
