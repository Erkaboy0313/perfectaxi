from django.http import JsonResponse
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import viewsets, mixins,response,status
from users import serializers
from PerfectTaxi.exceptions import BaseAPIException
from users.permissions import IsActive, IsAdmin, CanResetPassword, IsDeveloper
from PerfectTaxi.models import BaseSuccess
from .models import Client, User, Driver
from rest_framework.response import Response

# Create your views here.
@method_decorator(transaction.non_atomic_requests, name='dispatch')
class AuthViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @transaction.atomic
    @action(methods=['post'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = serializers.RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return response.Response({'user_id':data[1].id,'message':data[0]},status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def login(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)

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
        return response.Response({'user_id':data[1].id,'message':data[0]},status=status.HTTP_200_OK)

    @action(methods=['post'],detail=False)
    def test_verify(self,request,*args,**kwargs):
        serializer = serializers.TestVerifySerializer(data=request.data)
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

    @action(methods=['post'],detail=False)
    def verify(self,request,*args,**kwargs):
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

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsActive])
    def logout(self, request, *args, **kwargs):
        request.auth.delete()
        return JsonResponse(BaseSuccess().to_dict())

@method_decorator(transaction.non_atomic_requests, name='dispatch')
class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.select_related('user').prefetch_related('car_images').prefetch_related('car_tex_passport_images').prefetch_related('license_images')
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
    http_method_names = ['put','patch','delate','get']

    def list(self, request, *args, **kwargs):
        if request.user.is_admin:
            return super().list(request, *args, **kwargs)
        else:
            driver = Client.objects.select_related("user").get(user = request.user)
            serializer = self.get_serializer(driver)
            return Response(serializer.data)

