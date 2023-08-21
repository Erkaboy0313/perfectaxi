from django.shortcuts import render
from order.serializers import OrderSeriazer
from users.models import Client




def createOrder(user,data):
    client = Client.objects.get(user=user)
    serializer = OrderSeriazer(data=data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(client = client)
    serializer = OrderSeriazer(data)
    return serializer.data


# Create your views here.
