from rest_framework import viewsets,response,status
from users.permissions import IsActive
from creditCard.models import Card
from users.models import Client
from PerfectTaxi.exceptions import BaseAPIException
from .models import Balance
from .serializers import BalanceSerializer
# Create your views here.


class ChangePaymentMethodView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def create(self,request):
        payment_type = request.data.get('payment_type','')
        client = Client.objects.get(user = request.user)
        if payment_type == 'card':
            if Card.objects.filter(user = client).exists():
                client.payment_type = payment_type
                client.save()
            else:
                raise BaseAPIException('use have no card')
        elif payment_type == 'cash':
            client.payment_type = payment_type
            client.save()
        else:
            raise BaseAPIException('invalid payment type')
        return response.Response({"message":"payment type changed"},status=status.HTTP_200_OK)

class BalanceView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def list(self,request):
        if request.user.role == 'driver':
            balance = Balance.objects.get(driver__user = request.user)
            serializer = BalanceSerializer(balance)
            return response.Response(serializer.data,status=status.HTTP_200_OK)
        elif request.user.role =='admin':
            balance = Balance.objects.all()
            serializer = BalanceSerializer(balance,many=True)
            return response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            raise BaseAPIException('method not allowed')