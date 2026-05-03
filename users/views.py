from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes

from utils.responses import SuccessResponseMixin, success_response
from PerfectTaxi.exceptions import BaseAPIException
from users.permissions import IsActive, IsAdmin, CanChangeStatus
from .models import Client, User, Driver, DriverAvailableService
from payment.models import Balance
from users import serializers


@method_decorator(transaction.non_atomic_requests, name='dispatch')
@extend_schema_view(
    verify_number=extend_schema(
        summary="Verify phone number",
        description="Registers or verifies a user's phone number. Returns a user ID and message.",
        request=serializers.RegistrationSerializer,
        responses={200: {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'example': 123},
                'message': {'type': 'string', 'example': 'Verification successful'}
            }
        }},
    ),
    test_verify_code=extend_schema(
        summary="Test verification code",
        description="Used for testing code verification flow.",
        request=serializers.TestVerifySerializer,
        responses={200: serializers.TestVerifySerializer},
    ),
    verify_code=extend_schema(
        summary="Verify code",
        description="Validates the verification code sent to the user. Handles errors if code invalid.",
        request=serializers.VerifySerializer,
        responses={200: {'type': 'object'}},
    ),
    activate=extend_schema(
        summary="Activate user (Admin only)",
        description="Activates a driver user and initializes balance. Requires admin permissions.",
        responses={200: {
            'type': 'object',
            'properties': {'message': {'type': 'string', 'example': 'user activated'}}
        }},
    ),
    logout=extend_schema(
        summary="Logout user",
        description="Deletes user auth token. Requires user to be active.",
        responses={200: {'type': 'object', 'properties': {'success': {'type': 'boolean'}}}},
    ),
)
class AuthViewSet(SuccessResponseMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'verify_number':
            return serializers.RegistrationSerializer
        elif self.action == 'test_verify_code':
            return serializers.TestVerifySerializer
        elif self.action == 'verify_code':
            return serializers.VerifySerializer
        return serializers.RegistrationSerializer

    @transaction.atomic
    @action(methods=['post'], detail=False)
    def verify_number(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response({'user_id': data[1], 'message': data[0]})

    @action(methods=['post'], detail=False)
    def test_verify_code(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)

    @action(methods=['post'], detail=False)
    def verify_code(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.save()
        except (ValidationError, BaseAPIException):
            raise
        return Response(data)

    @action(methods=['post'], detail=True, permission_classes=[IsAdmin])
    def activate(self, request, *args, **kwargs):
        try:
            driver_id = kwargs['pk']
            driver = Driver.objects.select_related('user').get(id=driver_id)
            if not driver.user.is_verified:
                driver.user.is_verified = True
                driver.user.complete_profile = True
                driver.user.save()
                Balance.objects.create(driver=driver)
            return Response({'message': 'user activated'})
        except Exception:
            from utils.error_codes import DRIVER_NOT_FOUND
            raise BaseAPIException("Driver not found", code=DRIVER_NOT_FOUND)

    @transaction.atomic
    @action(methods=['post'], detail=False, permission_classes=[IsActive])
    def logout(self, request, *args, **kwargs):
        request.auth.delete()
        return success_response()


@method_decorator(transaction.non_atomic_requests, name='dispatch')
@extend_schema_view(
    list=extend_schema(
        summary="Get driver profile",
        description="Returns the profile of the currently authenticated driver.",
        responses={200: serializers.DriverProfileSerialzer},
        tags=["Drivers"],
    ),
    partial_update=extend_schema(
        summary="Update driver profile",
        description="Partially updates the logged-in driver's profile.",
        request=serializers.DriverSerializer,
        responses={200: {'type': 'object', 'properties': {"message": {'type': 'string', 'example': 'user updated'}}}},
        tags=["Drivers"],
    ),
)
class DriverViewSet(SuccessResponseMixin, viewsets.ModelViewSet):
    queryset = Driver.objects.select_related('user').prefetch_related(
        'car_images', 'car_tex_passport_images', 'license_images'
    )
    serializer_class = serializers.DriverSerializer
    http_method_names = ['patch', 'delate', 'get']
    permission_classes = (IsActive,)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        driver = Driver.objects.select_related("user").get(user=request.user)
        serializer = serializers.DriverProfileSerialzer(driver, context={'request': request})
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Get client profile(s)",
        description="- **Regular user**: returns their own client profile",
        responses={200: serializers.ClientSerializer(many=True)},
        tags=["Clients"],
    ),
    create=extend_schema(
        summary="Complete / update client profile",
        description=(
            "Updates the logged-in client's profile information. "
            "This endpoint does NOT create a new client."
        ),
        request=serializers.ClientProfileUpdateSerializer,
        responses={200: serializers.ClientSerializer},
        tags=["Clients"],
    ),
)
class ClientViewSet(SuccessResponseMixin, viewsets.ModelViewSet):
    queryset = Client.objects.select_related('user')
    serializer_class = serializers.ClientSerializer
    permission_classes = (IsActive,)
    http_method_names = ['post', 'get']

    def create(self, request, *args, **kwargs):
        serializer = serializers.ClientProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client = Client.objects.select_related("user").get(user=request.user)
        client.user.first_name = serializer.validated_data['first_name']
        client.user.last_name = serializer.validated_data['last_name']

        if not client.user.complete_profile:
            client.user.complete_profile = True

        client.user.save()
        return Response(self.get_serializer(client).data)

    def list(self, request, *args, **kwargs):
        client = Client.objects.select_related("user").get(user=request.user)
        serializer = self.get_serializer(client)
        return Response(serializer.data)


@extend_schema_view(
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Driver available service ID'
            )
        ]
    ),
    partial_update=extend_schema(
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Driver available service ID'
            )
        ]
    )
)
class DriverAvailabelServiceView(SuccessResponseMixin, viewsets.ModelViewSet):
    http_method_names = ['get', 'patch']
    permission_classes = (IsActive, CanChangeStatus)
    serializer_class = serializers.DriverServiceSerializer

    def get_queryset(self):
        return DriverAvailableService.objects.filter(driver__user=self.request.user)


@extend_schema(
    summary="Register / update FCM push token",
    description=(
        "Saves the device's FCM token against the authenticated user. "
        "Call this on every app launch or whenever the token is refreshed by the FCM SDK. "
        "The token is used to deliver push notifications (e.g. new order alerts for drivers).\n\n"
        "**Error cases:**\n"
        "- `401 Unauthorized` — missing or invalid `Authorization: Token <key>` header.\n"
        "- `400 Bad Request` — `fcm_token` field missing or exceeds 255 characters.\n"
    ),
    request=serializers.FCMTokenSerializer,
    responses={
        204: None,
        400: {
            'type': 'object',
            'properties': {
                'fcm_token': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'example': ['This field is required.'],
                }
            },
        },
        401: {
            'type': 'object',
            'properties': {
                'detail': {'type': 'string', 'example': 'Authentication credentials were not provided.'}
            },
        },
    },
)
class FCMTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request):
        serializer = serializers.FCMTokenSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=204)
