from datetime import datetime
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.utils import timezone
import uuid


from PerfectTaxi.exceptions import BaseAPIException

from .models import User,Driver,Client,Admin,Code


class RegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['client', 'driver'])
    name = serializers.CharField(required=True)
    phone = serializers.CharField()
 
    class Meta:
        model = User
        fields = ['role', 'name', 'phone']

    def create(self, validated_data):
        if User.objects.exist_user(validated_data):
            raise BaseAPIException("Foydalanuvchi allaqachon ro'yxatdan o'tgan")
        username = f"{validated_data['role']}_{validated_data['phone']}"
        validated_data['username'] = username
        self.instance = super().create(validated_data)
        if self.instance.role == self.instance.UserRole.DRIVER:
            user = Driver.objects.create(user = self.instance)
        elif self.instance.role == self.instance.UserRole.CLIENT:
            user = Client.objects.create(user = self.instance)

        code,created = Code.objects.get_or_create(user=self.instance)
        if not created:
            code.save()
        # data = send_verification_sms(user.phone,code.number)
        # return data[1]
        return ('kod yuborildi',user)

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    role = serializers.CharField()
    class Meta:
        fields = ['phone','role']

    def save(self, **kwargs):
        data = self.validated_data
        try:
            user: User = User.objects.get(phone=data['phone'],role=data['role'])
        except BaseException:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        if user.blocked_at:
            raise BaseAPIException("Foydalanuvchi bloklangan")
        
        if data['role'] == user.UserRole.DRIVER:
            r_user = Driver.objects.get(user=user)
        if data['role'] == user.UserRole.CLIENT:
            r_user = Client.objects.get(user=user)
        

        code,created = Code.objects.get_or_create(user=user)
        if not created:
            code.save()
        # data = send_verification_sms(user.phone,code.number)
        # return data[1]
        return ('kod yuborildi',r_user)

class TestVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    user = serializers.IntegerField()
    role = serializers.CharField()

    def save(self,**kwargs):
        data = self.validated_data
        try:
            if data['role'] == "driver":
                user = Driver.objects.get(id = data['user']).user
            elif data['role'] == "client":
                user = Client.objects.get(id = data['user']).user
        except BaseException:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        if int(data['code']) != 66666:
            raise BaseAPIException('Kod notogri kiritildi')
        if user.blocked_at:
            raise BaseAPIException("Foydalanuvchi bloklangan")
        if not user.confirmed_at:
            user.confirm
        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key}

class VerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    user = serializers.IntegerField()

    def save(self,**kwargs):
        data = self.validated_data
        try:
            user: User = User.objects.get(id = user)
            orginal_code = Code.objects.get(user = user)
            if int(self.validated_data['code']) != orginal_code.number:
                raise BaseAPIException('Kod notogri kiritildi')
        except BaseException:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        if user.blocked_at:
            raise BaseAPIException("Foydalanuvchi bloklangan")

        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key}

class DriverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Driver
        exclude = ['user']





















