from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Services
from .serializers import ServiceSerializer

class ServicesView(viewsets.ViewSet):

    def list(self,request):
        services = Services.objects.all()
        serializer = ServiceSerializer(services,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)