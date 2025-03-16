from users.models import User,Driver,Client,DriverAvailableService,DocumentImages
from payment.models import Balance
from rest_framework import serializers
from PerfectTaxi.exceptions import BaseAPIException
from order.models import Order,RejectReason,Services
from category.models import CarService
from payment.models import Balance,Payment
from .models import AdminChatRoom,Message
from django.db import IntegrityError
from users.serializers import DriverServiceSerializer
from category.serializers import CarModelSerializer,ColorSerializer,CarBrendSerializer

class AdminChatRoomSerializer(serializers.ModelSerializer):
    user_phone = serializers.ReadOnlyField()
    class Meta:
        model = AdminChatRoom
        fields = ['id','title','closed','user_phone']
        read_only_fields = ('closed',)
        
class MessageUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_admin'] = instance.is_admin
        return data 

class MessageSerializer(serializers.ModelSerializer):
    author = MessageUserSerializer(read_only = True)
    
    class Meta:
        model = Message
        fields = '__all__'
    
class RejectReasonSerialzier(serializers.ModelSerializer):
    class Meta:
        model = RejectReason
        fields = '__all__'

class CarServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarService
        fields = '__all__'

class SerivceSeriazer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','role','first_name','last_name','phone',"confirmed_at","blocked_at","reason","is_block","complete_profile","is_verified"]

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = DocumentImages  # Your document images model
        fields = ['image']

    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url

class DriverRegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    car_images = ImageSerializer(many = True,read_only=True)
    car_tex_passport_images = ImageSerializer(many = True,read_only=True)
    license_images = ImageSerializer(many = True,read_only=True)
    avilable_service = DriverServiceSerializer(many = True, read_only = True)

    class Meta:
        model = Driver
        fields = ['id','user', 'profile_image', 'car_model', 'car_name', 'car_number', 'car_color', 'car_manufactured_date', 
                  'car_tex_passport_date','license_date','luggage','airconditioner','inmark','mark','status',"car_images","car_tex_passport_images","license_images",'avilable_service']

    def create(self, validated_data):
        # Extract user data from validated_data
        user_data = validated_data.pop('user')
        
        username = f"{user_data['role']}_{user_data['phone']}"
        user_data['username'] = username
        
        try:
            base_user,created = User.objects.get_or_create(**user_data)
        except IntegrityError:
            raise BaseAPIException("User Already Registered with this phone")
        except Exception as e:
            print(f"some thing went wrong {e}")
            raise BaseAPIException("server error")
        
        # Create the Driver instance and associate it with the User
        driver = Driver.objects.create(user=base_user, **validated_data)
        Balance.objects.create(driver = driver)
        
        # Return the Driver instance
        return {"id":driver.id}
    
    def update(self, instance, validated_data):
        # Handle nested `user` update
        user_data = validated_data.pop('user', None)
        if user_data:
            user_instance = instance.user
            for attr, value in user_data.items():
                setattr(user_instance, attr, value)
            user_instance.save()
        print(validated_data)
        # Update other Driver fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['car_model'] = CarBrendSerializer(instance.car_model).data
        data['car_name'] = CarModelSerializer(instance.car_name).data
        data['car_color'] = ColorSerializer(instance.car_color).data
        return data

class DriverUploadImageSerializer(serializers.Serializer):
    profile_image = serializers.FileField(write_only=True, required=False)
    car_images = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    car_tex_passport_images = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    license_images = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)

    def save(self, driver:Driver):
        profile_image = self.validated_data.get('profile_image')
        car_images = self.validated_data.get('car_images', [])
        car_tex_passport_images = self.validated_data.get('car_tex_passport_images', [])
        license_images = self.validated_data.get('license_images', [])
        
        if profile_image:
            driver.profile_image = profile_image
            driver.save(update_fields=['profile_image'])


        return self.save_images(driver, car_images, car_tex_passport_images, license_images)

    def save_images(self, obj, car_images, car_tex_passport_images, license_images):
        images_data = {
            "car_images": (obj.car_images, car_images),
            "car_tex_passport_images": (obj.car_tex_passport_images, car_tex_passport_images),
            "license_images": (obj.license_images, license_images),
        }

        saved_images = {}

        for field, (related_manager, images) in images_data.items():
            if images:
                related_manager.clear()
                saved_images[field] = []
                for image in images:
                    img = DocumentImages.objects.create(image=image)
                    related_manager.add(img)
                    saved_images[field].append(img.id)

        return saved_images

class DriverShortSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)  # Assuming the phone field is in User

    class Meta:
        model = Driver
        fields = ['car_number', 'first_name', 'last_name', 'phone']

class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Client
        fields = ['user']

class ClientShortSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)  # Assuming the phone field is in User

    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'phone']

class OrderDetailSerializer(serializers.ModelSerializer):

    client = ClientShortSerializer()
    driver = DriverShortSerializer()
    carservice = CarServiceSerializer()
    reject_reason = RejectReasonSerialzier()
    services = SerivceSeriazer(many=True)

    class Meta:
        model = Order
        fields = '__all__'

class StatisticsSeriarlizer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()

class BalanceSerializer(serializers.ModelSerializer):
    driver = DriverShortSerializer()
    class Meta:
        model = Balance
        fields = '__all__'

class PaymentSeriazer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

