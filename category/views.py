from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from utils.responses import SuccessResponseMixin, error_response
from utils.error_codes import METHOD_NOT_ALLOWED
from users.permissions import IsActive
from users.models import Client
from .serializers import (
    CarServiceSerializer, SavedLocationsSerializer,
    CarBrendSerializer, CarModelSerializer, ColorSerializer,
)
from .models import CarService, SavedLocation, CarBrend, CarModel, Color


class CarSeriviceView(SuccessResponseMixin, viewsets.ModelViewSet):
    queryset = CarService.objects.all()
    serializer_class = CarServiceSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


class SavedLocationView(SuccessResponseMixin, viewsets.ModelViewSet):
    queryset = SavedLocation.objects.all()
    serializer_class = SavedLocationsSerializer
    http_method_names = ['get', 'post', 'put']
    permission_classes = (IsActive,)

    def get_queryset(self):
        if self.request.user.role == "client":
            return self.queryset.filter(user__user=self.request.user)
        if self.request.user.role == "admin":
            return self.queryset

    def list(self, request, *args, **kwargs):
        if request.user.role == "driver":
            return error_response(METHOD_NOT_ALLOWED, "Method not allowed for drivers", status=403)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        client = Client.objects.get(user=self.request.user)
        serializer.save(user=client)


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
class CarBrendViewSet(SuccessResponseMixin, viewsets.ViewSet):

    def list(self, request):
        queryset = CarBrend.objects.all()
        serializer = CarBrendSerializer(queryset, many=True)
        from rest_framework.response import Response
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        brand_id = self.kwargs.get("pk")
        car_models = CarModel.objects.filter(brend__id=brand_id)
        serializer = CarModelSerializer(car_models, many=True)
        from rest_framework.response import Response
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List colors",
        description="Returns a list of all available car colors.",
        responses={200: ColorSerializer(many=True)}
    )
)
class ColorViewSet(SuccessResponseMixin, viewsets.ViewSet):

    def list(self, request):
        queryset = Color.objects.all()
        serializer = ColorSerializer(queryset, many=True)
        from rest_framework.response import Response
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all car models",
        description="Returns a list of all car models regardless of brand.",
        responses={200: CarModelSerializer(many=True)}
    )
)
class CarModelViewSet(SuccessResponseMixin, viewsets.ViewSet):

    def list(self, request):
        queryset = CarModel.objects.all()
        serializer = CarModelSerializer(queryset, many=True)
        from rest_framework.response import Response
        return Response(serializer.data)
