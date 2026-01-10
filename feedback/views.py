from rest_framework import viewsets,response,status
from .serializers import FeedbackSerializer,ResonSerializer,Reson
from users.permissions import IsActive
from users.models import Driver
from .tasks import calculate_mark
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    create=extend_schema(
        summary="Submit feedback",
        description=(
            "Allows a client or driver to submit feedback for an order. "
            "The feedback type is automatically assigned based on the user role."
        ),
        request=FeedbackSerializer,
        responses={200: FeedbackSerializer},
    ),
    list=extend_schema(
        summary="Get driver mark",
        description="Returns the driver's rating. Only accessible for users with role 'driver'.",
        responses={200: {'type': 'object', 'properties': {'mark': {'type': 'number', 'example': 4.5}}}},
    )
)
class FeedBackView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def create(self,request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.role == 'client':
            feedback_type = 'client'
            
        elif request.user.role == 'driver':
            feedback_type = 'driver'

        serializer.save(type= feedback_type)
        
        if feedback_type == 'client':
            calculate_mark.delay(serializer.instance.order.driver.id)
            
        return response.Response(serializer.data,status=status.HTTP_200_OK)
        
    def list(self,request):
        if request.user.role == 'driver':
            driver = Driver.objects.get(user = request.user).mark
            return response.Response({"mark":driver},status=status.HTTP_200_OK)
        else:
            return response.Response({"error":"method not allowed"},status=status.HTTP_403_FORBIDDEN)


@extend_schema_view(
    feedback=extend_schema(
        summary="Get problem reasons",
        description="Returns a list of reasons categorized as problems for feedback purposes.",
        responses={200: ResonSerializer(many=True)}
    ),
    comfort=extend_schema(
        summary="Get comfort reasons",
        description="Returns a list of reasons categorized as comfort for feedback purposes.",
        responses={200: ResonSerializer(many=True)}
    ),
)
class ReasonView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    @action(methods=['GET'],detail=False)
    def feedback(self,request):
        reasons = Reson.objects.filter(type = Reson.ResonType.PROBLEM)
        serializer = ResonSerializer(reasons,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['GET'],detail=False)
    def comfort(self,request):
        reasons = Reson.objects.filter(type = Reson.ResonType.COMFORT)
        serializer = ResonSerializer(reasons,many=True)
        return response.Response(serializer.data,status=status.HTTP_200_OK)
