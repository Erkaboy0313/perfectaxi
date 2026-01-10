from rest_framework import viewsets,response,status
from users.permissions import IsActive
from creditCard.models import Card
from users.models import Client
from PerfectTaxi.exceptions import BaseAPIException
from .models import Balance
from .serializers import BalanceSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import serializers


class ChangePaymentMethodRequestSerializer(serializers.Serializer):
    payment_type = serializers.ChoiceField(
        choices=['card', 'cash']
    )

class ChangePaymentMethodResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

@extend_schema_view(
    create=extend_schema(
        summary="Change payment method",
        description=(
            "Allows a client to change their payment method to 'card' or 'cash'. "
            "If 'card' is chosen, the user must have a saved card."
        ),
        request=ChangePaymentMethodRequestSerializer,
        responses={200: ChangePaymentMethodResponseSerializer},
        tags=['Client'],
    )
)
class ChangePaymentMethodView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def create(self, request):
        serializer = ChangePaymentMethodRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_type = serializer.validated_data['payment_type']
        client = Client.objects.get(user=request.user)

        if payment_type == 'card':
            if Card.objects.filter(user=client).exists():
                client.payment_type = payment_type
                client.save()
            else:
                raise BaseAPIException('user has no card')
        else:  # cash
            client.payment_type = payment_type
            client.save()

        return response.Response(
            {"message": "payment type changed"},
            status=status.HTTP_200_OK
        )
    
@extend_schema_view(
    list=extend_schema(
        summary="Get balance",
        description=(
            "Returns balance info. "
            "Drivers: their own balance if verified. "
            "Admins: all balances."
        ),
        responses={200: BalanceSerializer(many=True)},
    )
)
class BalanceView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def list(self,request):
        if request.user.role == 'driver':
            if request.user.is_verified:
                balance = Balance.objects.get(driver__user = request.user)
                serializer = BalanceSerializer(balance)
                return response.Response(serializer.data,status=status.HTTP_200_OK)
            else:
                raise BaseAPIException("you are not verified")
        elif request.user.role =='admin':
            balance = Balance.objects.all()
            serializer = BalanceSerializer(balance,many=True)
            return response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            raise BaseAPIException('method not allowed')