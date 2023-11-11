from rest_framework import serializers
from .models import Card
from PerfectTaxi.exceptions import BaseAPIException


class CreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        exclude = ['user','verified']

    def validate_cardNumber(self,value):
        if not value.isdigit() or not len(value) == 16:
            raise BaseAPIException('invalid Card number')
        else:
            return value
        
    def validate_cardExpireDate(self,value):
        if not len(value) == 5 or int(value.split('/')[1]) < 23:
            raise BaseAPIException('invalid expire data')
        else:
            return value