from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.conf import settings

from PerfectTaxi.exceptions import BaseAPIException

from .models import User,Driver,Client,Admin,Code,DocumentImages


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name','phone']

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
            if int(data['code']) != 66666:
                raise BaseAPIException('Kod notogri kiritildi')
            if user.blocked_at:
                raise BaseAPIException("Foydalanuvchi bloklangan")
            if not user.confirmed_at:
                user.confirm
        except BaseException:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key}

class VerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    user = serializers.IntegerField()
    
    def save(self,**kwargs):
        try:
            user: User = User.objects.get(id = user)
            orginal_code = Code.objects.get(user = user)
            if int(self.validated_data['code']) != orginal_code.number:
                raise BaseAPIException('Kod notogri kiritildi')
            if user.blocked_at:
                raise BaseAPIException("Foydalanuvchi bloklangan")
        except BaseException:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        if user.blocked_at:
            raise BaseAPIException("Foydalanuvchi bloklangan")
        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key}
    
class DocumentImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImages
        fields = ['image']

class DriverSerializer(serializers.ModelSerializer):
    car_images = serializers.ListField(child = serializers.FileField(),write_only = True)
    car_tex_passport_images = serializers.ListField(child = serializers.FileField(),write_only = True)
    license_images = serializers.ListField(child = serializers.FileField(),write_only = True)
    user = UserSerializer()
    class Meta:
        model = Driver
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True},
            'user': {'read_only': True}
            }
        depth = 1

    
    def save(self, **kwargs):
        car_images = self.validated_data.pop('car_images',[])
        car_tex_passport_images = self.validated_data.pop('car_tex_passport_images',[])
        license_images = self.validated_data.pop('license_images',[])
        obj = super().save(**kwargs)
        self.save_images(obj,car_images,car_tex_passport_images,license_images)
        return obj
    
    def save_images(self,obj,car_images,car_tex_passport_images,license_images):
        if car_images:
            obj.car_images.clear()
            for image in car_images:
                img = DocumentImages.objects.create(image = image)
                obj.car_images.add(img)
        if car_tex_passport_images:
            obj.car_tex_passport_images.clear()
            for image in car_tex_passport_images:
                img = DocumentImages.objects.create(image = image)
                obj.car_tex_passport_images.add(img)
        if license_images:
            obj.license_images.clear()
            for image in license_images:
                img = DocumentImages.objects.create(image = image)
                obj.license_images.add(img)

    def to_representation(self, instance):
        request = self._kwargs['context']['request']
        obj = super().to_representation(instance)
        if request.user.is_admin():
            obj['car_images'] = [f"{settings.HOST}{x.image.url}" for x in instance.car_images.all()]
            obj['car_tex_passport_images'] = [f"{settings.HOST}{x.image.url}" for x in instance.car_tex_passport_images.all()]
            obj['license_images'] = [f"{settings.HOST}{x.image.url}" for x in instance.license_images.all()]
        for key,value in obj['user'].items():
            obj[key] = value
        del obj['user']
        return obj

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Client
        fields = ['id','user','payment_type']
        extra_kwargs = {
            'user':{"read_only":True}
        }
    
    def to_representation(self, instance):
        obj = super().to_representation(instance)
        for key,value in obj['user'].items():
            obj[key] = value
        del obj['user']
        return obj
