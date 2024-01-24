from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.conf import settings
from PerfectTaxi.exceptions import BaseAPIException
from .models import User,Driver,Client,Code,DocumentImages,DriverAvailableService
from feedback.tasks import populate_mark

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','phone']

class RegistrationSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=['client', 'driver'])
    phone = serializers.CharField()
 
    class Meta:
        model = User
        fields = ['role', 'phone']

    def create(self, validated_data):
        username = f"{validated_data['role']}_{validated_data['phone']}"
        validated_data['username'] = username
        base_user,created = User.objects.get_or_create(**validated_data)
        if created:
            if base_user.role == base_user.UserRole.DRIVER:
                user = Driver.objects.create(user = base_user)
            elif base_user.role == base_user.UserRole.CLIENT:
                user = Client.objects.create(user = base_user)
        else:
            if base_user.role == base_user.UserRole.DRIVER:
                user = Driver.objects.get(user = base_user)
            elif base_user.role == base_user.UserRole.CLIENT:
                user = Client.objects.get(user = base_user)

        code,created = Code.objects.get_or_create(user=base_user)
        
        if not created:
            code.save()

        # ---------- Send Verification code ------------#
        # data = send_verification_sms(user.phone,code.number)
        # return data[1]

        return ('kod yuborildi',user.id)

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
            
            #temporary should be specific login for admin.
            elif data['role'] == 'admin':
                user = User.objects.get(id = data['user'])
                
            if int(data['code']) != 66666:
                raise BaseAPIException('Kod notogri kiritildi')
            if user.blocked_at:
                raise BaseAPIException("Foydalanuvchi bloklangan")
            if not user.confirmed_at:
                user.confirm
        except BaseException as e:
            raise BaseAPIException("Foydalanuvchi topilmadi")
        token, __ = Token.objects.get_or_create(user=user)
        return {'token': token.key, "profile":user.complete_profile}

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
    first_name = serializers.CharField(write_only = True)
    last_name = serializers.CharField(write_only = True)
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
        obj.user.first_name = self.validated_data['first_name']
        obj.user.last_name = self.validated_data['last_name']
        obj.user.complete_profile = True
        obj.user.save()
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

class DriverInfoSeriazer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    class Meta:
        model = Driver
        fields = ['name','phone','car_name','car_number','car_color']

class DriverServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverAvailableService
        fields = '__all__'
