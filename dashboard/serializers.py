from users.models import User,Driver,Client,DriverAvailableService,DocumentImages
from payment.models import Balance
from rest_framework import serializers
from PerfectTaxi.exceptions import BaseAPIException
from order.models import Order,RejectReason,Services
from category.models import CarService
from payment.models import Balance,Payment


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

class DriverRegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    car_images = serializers.ListField(child = serializers.FileField(),write_only = True,required = False)
    car_tex_passport_images = serializers.ListField(child = serializers.FileField(),write_only = True,required = False)
    license_images = serializers.ListField(child = serializers.FileField(),write_only = True,required = False)

    class Meta:
        model = Driver
        fields = ['id','user', 'profile_image', 'car_model', 'car_name', 'car_number', 'car_color', 'car_manufactured_date', 
                  'car_tex_passport_date', 'license_date', 'luggage', 'airconditioner', 'inmark', 'mark', 'status', 
                  'car_images', 'car_tex_passport_images', 'license_images']

    def create(self, validated_data):
        # Extract user data from validated_data
        user_data = validated_data.pop('user')
        car_images = self.validated_data.pop('car_images',[])
        car_tex_passport_images = self.validated_data.pop('car_tex_passport_images',[])
        license_images = self.validated_data.pop('license_images',[])
        
        username = f"{user_data['role']}_{user_data['phone']}"
        user_data['username'] = username
        base_user,created = User.objects.get_or_create(**user_data)

        if not created:
            raise BaseAPIException("User Already Registered")
        
        # Create the Driver instance and associate it with the User
        driver = Driver.objects.create(user=base_user, **validated_data)
        Balance.objects.create(driver = driver)
        self.save_images(driver,car_images,car_tex_passport_images,license_images)
        
        # Return the Driver instance
        return driver
    
    def save_images(self,obj:Driver,car_images,car_tex_passport_images,license_images):
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
        data = super().to_representation(instance)
        data['car_images'] = ImageSerializer(instance.car_images.all(),many=True).data
        data['car_tex_passport_images'] = ImageSerializer(instance.car_tex_passport_images.all(),many=True).data
        data['license_images'] = ImageSerializer(instance.license_images.all(),many=True).data
        return data
    
class DriverShortSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)  # Assuming the phone field is in User

    class Meta:
        model = Driver
        fields = ['car_number', 'first_name', 'last_name', 'phone']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentImages
        fields = ['image']

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

