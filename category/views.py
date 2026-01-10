from rest_framework import response,status
from rest_framework import viewsets,permissions
from .serializers import *
from users.permissions import IsActive
from users.models import Client
from drf_spectacular.utils import extend_schema, extend_schema_view  , OpenApiParameter, OpenApiTypes

class CarSeriviceView(viewsets.ModelViewSet):
    queryset = CarService.objects.all()
    serializer_class = CarServiceSerializer
    http_method_names = ['get','post','put','delete']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]

class SavedLocationView(viewsets.ModelViewSet):
    queryset = SavedLocation.objects.all()
    serializer_class = SavedLocationsSerializer
    http_method_names = ['get','post','put']
    permission_classes = (IsActive,)

    def get_queryset(self):
        if self.request.user.role == "client":
            return self.queryset.filter(user__user = self.request.user)
        if self.request.user.role == "admin":
            return self.queryset

    def list(self, request, *args, **kwargs):
        if request.user.role != "driver":
            return super().list(request, *args, **kwargs)
        else:
            return response.Response({"error":"method not allowed"},status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        client = Client.objects.get(user = self.request.user)
        serializer.save(user = client)

@extend_schema_view(
    list=extend_schema(
        summary="List car brands",
        operation_id="carbrand_list",
        responses={200: CarBrendSerializer(many=True)},
        tags=['Cars'],
    ),
    retrieve=extend_schema(
        summary="List models by brand",
        operation_id="carbrand_retrieve",
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Car brand ID',
            )
        ],
        responses={200: CarModelSerializer(many=True)},
        tags=['Cars'],
    ),
)
class CarBrendViewSet(viewsets.ViewSet):

    def list(self,request):
        queryset = CarBrend.objects.all()
        serializer = CarBrendSerializer(queryset,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        brand_id = self.kwargs.get("pk")
        car_models = CarModel.objects.filter(brend__id = brand_id)
        serializer = CarModelSerializer(car_models,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

@extend_schema_view(
    list=extend_schema(
        summary="List colors",
        description="Returns a list of all available car colors.",
        responses={200: ColorSerializer(many=True)}
    )
)
class ColorViewSet(viewsets.ViewSet):

    def list(self,request):
        queryset = Color.objects.all()
        serializer = ColorSerializer(queryset,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

@extend_schema_view(
    list=extend_schema(
        summary="List all car models",
        description="Returns a list of all car models regardless of brand.",
        responses={200: CarModelSerializer(many=True)}
    )
)
class CarModelViewSet(viewsets.ViewSet):

    def list(self,request):
        queryset = CarModel.objects.all()
        serializer = CarModelSerializer(queryset,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

