from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import viewsets,response,status
from users import serializers
from PerfectTaxi.exceptions import BaseAPIException
from users.permissions import IsActive, IsAdmin, CanChangeStatus
from PerfectTaxi.models import BaseSuccess
from .models import Client, User, Driver, DriverAvailableService
from payment.models import Balance
from rest_framework.response import Response

# Create your views here.
@method_decorator(transaction.non_atomic_requests, name='dispatch')
class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @transaction.atomic
    @action(methods=['post'], detail=False)
    def verify_number(self, request, *args, **kwargs):
        serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response.Response({'user_id':data[1],'message':data[0]},status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False)
    def test_verify_code(self,request,*args,**kwargs):
        serializer = serializers.TestVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response.Response(data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False)
    def verify_code(self,request,*args,**kwargs):
        serializer = serializers.VerifySerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.save()
        except ValidationError:
            # message = controllers.errors_to_string(serializer.errors)
            # error_authentication_log(request.data.get('email'), message)
            raise
        except BaseAPIException as e:
            # error_authentication_log(request.data.get('email'), e.args[0])
            raise
        return response.Response(data,status=status.HTTP_200_OK)

    @action(methods=['post'],detail=True,permission_classes=[IsAdmin])
    def activate(self,request,*args,**kwargs):
        try:
            driver_id = kwargs['pk']
            driver = Driver.objects.select_related('user').get(id = driver_id)
            if not driver.user.is_verified:
                driver.user.is_verified = True
                driver.user.save()
                Balance.objects.create(driver = driver)
            return Response({'message':"user activated"},status=status.HTTP_200_OK)
        except:
            raise BaseAPIException("Foydalanuvchi topilmadi")

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsActive])
    def logout(self, request, *args, **kwargs):
        request.auth.delete()
        return JsonResponse(BaseSuccess().to_dict())

@method_decorator(transaction.non_atomic_requests, name='dispatch')
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.select_related('user').prefetch_related('car_images','car_tex_passport_images','license_images')
    serializer_class = serializers.DriverSerializer
    http_method_names = ['put','patch','delate','get']
    permission_classes = (IsActive,)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        if request.user.is_admin():
            return super().list(request, *args, **kwargs)
        else:
            driver = Driver.objects.select_related("user").get(user = request.user)
            serializer = self.get_serializer(driver)
            return Response(serializer.data)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.select_related('user')
    serializer_class = serializers.ClientSerializer
    permission_classes = (IsActive,)
    http_method_names = ['post','patch','delate','get']

    def create(self, request, *args, **kwargs):
        first_name,last_name = request.data.get('first_name',None),request.data.get('last_name',None)
        client = Client.objects.select_related("user").get(user = request.user)
        client.user.first_name = first_name
        client.user.last_name = last_name
        if client.user.first_name and client.user.last_name and client.user.complete_profile == False:
            client.user.complete_profile = True
        client.user.save()
        serializer = self.get_serializer(client)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        if request.user.is_admin:
            return super().list(request, *args, **kwargs)
        else:
            client = Client.objects.select_related("user").get(user = request.user)
            serializer = self.get_serializer(client)
            return Response(serializer.data)

class DriverAvailabelServiceView(viewsets.ModelViewSet):
    http_method_names = ['get','post']
    permission_classes = (IsActive,CanChangeStatus)
    serializer_class = serializers.DriverServiceSerializer
    
    def get_queryset(self):
        return DriverAvailableService.objects.filter(driver__user = self.request.user)
        