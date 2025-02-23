from rest_framework.viewsets import ModelViewSet,ViewSet
from .serializers import DriverRegisterSerializer,ClientSerializer,OrderDetailSerializer,\
    StatisticsSeriarlizer,BalanceSerializer,PaymentSeriazer,AdminChatRoomSerializer,MessageSerializer,\
        DriverUploadImageSerializer,DriverServiceSerializer,CarServiceSerializer
from users.models import Driver,Client
from users.permissions import IsAdmin,IsActive
from order.models import Order
from rest_framework.decorators import action
from django.db.models import Count
from rest_framework.response import Response
from rest_framework import status
from payment.models import Balance,Payment
from category.models import CarBrend,Color,CarModel
from category.serializers import CarBrendSerializer,ColorSerializer,CarModelSerializer
from rest_framework.authtoken.models import Token
from users.models import User,DriverAvailableService
from django.contrib.auth import authenticate
from PerfectTaxi.exceptions import BaseAPIException
from .models import AdminChatRoom,Message


class AdminLoginViewSet(ViewSet):

    def create(self,request,*args,**kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request=request,username=username,password=password)
        if user:
            if user.role == User.UserRole.ADMIN:
                token, __ = Token.objects.get_or_create(user=user)
                return Response({"token":token.key})
        raise BaseAPIException('User not found')
                
class DriverViewset(ModelViewSet):
    queryset = Driver.objects.select_related('user').prefetch_related('car_images','car_tex_passport_images','license_images')
    serializer_class = DriverRegisterSerializer
    # permission_classes = (IsAdmin,)
    
    def create(self, request, *args, **kwargs):

        serializer = DriverRegisterSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)
        
    def get_serializer_context(self):
        return {'request': self.request}
        
    @action(methods=['POST'], detail=True)
    def upload_photos(self, request, *args, **kwargs):
        driver_id = kwargs.get('pk')
        driver = Driver.objects.get(id=driver_id)
        serializer = DriverUploadImageSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        saved_images = serializer.save(driver=driver)

        return Response({"success": True, "saved_images": saved_images})

    @action(methods=['POST'],detail=True)
    def verify_driver(self,request,*args,**kwargs):
        driver_id = kwargs.get('pk')
        driver = Driver.objects.get(id = driver_id)
        driver.user.is_verified = not driver.user.is_verified
        driver.user.save()
        return Response({"success": True})
        
    @action(methods=['POST'],detail=True)
    def unblock_driver(self,request,*args,**kwargs):
        driver_id = kwargs.get('pk')
        driver = Driver.objects.get(id = driver_id)
        driver.user.is_block = False
        driver.user.reason = None
        driver.user.save()
        return Response({"success": True})
    
    @action(methods=['POST'],detail=True)
    def block_driver(self,request,*args,**kwargs):
        driver_id = kwargs.get('pk')
        reason = request.data.get("reason",None)
        driver = Driver.objects.get(id = driver_id)
        driver.user.is_block = True
        driver.user.reason = reason
        driver.user.save()
        return Response({"success": True})

    @action(methods=['POST'],detail=True)
    def add_service(self,request,*args,**kwargs):
        driver_id = kwargs.get('pk')
        service_list = request.data.get("service_list",[])
        
        DriverAvailableService.objects.filter(driver__id = driver_id).exclude(service__id__in = service_list).delete()
        
        for s_id in service_list:
            serializer = DriverServiceSerializer(data = {'driver':driver_id,'service':s_id})
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except:
                pass
        return Response({"success": True})
        

class ClientViewSet(ModelViewSet):
    queryset = Client.objects.select_related('user')
    serializer_class = ClientSerializer
    # permission_classes = (IsAdmin,)

    @action(methods=['POST'],detail=True)
    def unblock_client(self,request,*args,**kwargs):
        client_id = kwargs.get('pk')
        client = Client.objects.get(id = client_id)
        client.user.is_block = False
        client.user.save()

    @action(methods=['POST'],detail=True)
    def block_client(self,request,*args,**kwargs):
        client_id = kwargs.get('pk')
        client = Client.objects.get(id = client_id)
        client.user.is_block = True
        client.user.save()

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.select_related("client",'client__user','driver','driver__user','carservice','reject_reason').prefetch_related('services')
    serializer_class = OrderDetailSerializer
    # permission_classes = (IsAdmin,)
    http_method_names = ['get','delete']

    def get_queryset(self):
        valid_data = ['client','driver','status','region_code']
        filter_data = {(f"{key}__user__phone__icontains" if key in ['client','driver'] else key) :value for key,value in self.request.GET.items() if key in valid_data}
        return self.queryset.filter(**filter_data)

    def list(self, request, *args, **kwargs):
        data = self.serializer_class(self.get_queryset(),many =True).data
        statistics = Order.objects.values('status').annotate(count = Count('status'))
        st_serializer = StatisticsSeriarlizer(statistics,many = True).data
        context = {
            'statistics' : st_serializer,
            'orders' : data
        }
        return Response(context,status=status.HTTP_200_OK)

class BalanceViewSet(ModelViewSet):
    queryset = Balance.objects.select_related('driver','driver__user')
    serializer_class = BalanceSerializer
    # permission_classes = (IsAdmin,)

    def get_queryset(self):
        available_keys = ['driver','balance_id']
        filter_data = {f"{key}__driver__user__phone__icontains" if key == 'driver' else f"{key}__icontains":value for key,value in self.request.GET.items() if key in available_keys}
        return self.queryset.filter(**filter_data)

class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSeriazer
    # permission_classes = (IsAdmin,)
    http_method_names = ['get','delete']

    def get_queryset(self):
        available_keys = ['balance_id']
        filter_data = {f"{key}__icontains":value for key,value in self.request.GET.items() if key in available_keys}
        return self.queryset.filter(**filter_data)

    def list(self, request, *args, **kwargs):
        statistics = Payment.objects.values('status').annotate(count = Count("status"))
        payments_data = self.serializer_class(self.get_queryset(),many=True).data
        statictics_data = StatisticsSeriarlizer(statistics,many=True).data
        context = {
            'statistics':statictics_data,
            'payment':payments_data
        }
        return Response(context)

class CarBrendViewSet(ModelViewSet):
    queryset = CarBrend.objects.all()
    serializer_class = CarBrendSerializer
    # permission_classes = (IsAdmin,)

class CarModelViewSet(ModelViewSet):
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    # permission_classes = (IsAdmin,)

class ColorViewSet(ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    # permission_classes = (IsAdmin,)

class AdminChatViewSet(ModelViewSet): 
    serializer_class = AdminChatRoomSerializer
    permission_classes = (IsActive,)
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return AdminChatRoom.objects.prefetch_related('users')  
        else:
            return AdminChatRoom.objects.filter(users=user).prefetch_related('users')

    def retrieve(self, request, *args, **kwargs):

        isntance = self.get_object()
        
        if request.user.is_admin() and request.user not in isntance.users.all():
            isntance.users.add(self.request.user)
            isntance.save()
            
        if not isntance.users.filter(id=self.request.user.id).exists():
            return Response(
                {"detail": "You are not a participant of this room."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        messages = Message.objects.filter(room = isntance)
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
    def perform_create(self, serializer):
        # Create a new chat room and add the authenticated user to it
        chat_room = serializer.save()
        chat_room.users.add(self.request.user)
        chat_room.save()
        
class MessageViewSet(ModelViewSet):
    queryset = Message.objects.select_related('room', 'author')
    serializer_class = MessageSerializer
    permission_classes = (IsActive,)

    def perform_create(self, serializer):

        user = self.request.user
        chat_room = serializer.validated_data.get('room')

        if not chat_room.users.filter(id=user.id).exists():
            return Response(
                {"detail": "You are not a participant of this room."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        serializer.save(author=user)
