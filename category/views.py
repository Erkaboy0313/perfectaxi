from django.shortcuts import render
from rest_framework import viewsets,permissions
from .serializers import *

class CarSeriviceView(viewsets.ModelViewSet):
    queryset = CarService.objects.all()
    serializer_class = CarServiceSerializer
    http_method_names = ['get','post','put']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

