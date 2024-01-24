from rest_framework import viewsets,response,status
from .serializers import FeedbackSerializer,ResonSerializer,Reson
from users.permissions import IsActive
from users.models import Client,Driver
from .tasks import calculate_mark
from rest_framework.decorators import action

class FeedBackView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def create(self,request):
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.role == 'client':
            feedback_type = 'client'
            client = Client.objects.get(user= request.user)
            feedback = serializer.save(client = client,type= feedback_type)
            calculate_mark.delay(feedback.driver.id)
            
        elif request.user.role == 'driver':
            feedback_type = 'driver'
            driver = Driver.objects.get(user= request.user)
            feedback = serializer.save(driver = driver,type= feedback_type)
            
        return response.Response(serializer.data,status=status.HTTP_200_OK)
        
    def list(self,request):
        if request.user.role == 'driver':
            driver = Driver.objects.get(user = request.user).mark
            return response.Response({"mark":driver},status=status.HTTP_200_OK)
        else:
            return response.Response({"error":"method not allowed"},status=status.HTTP_403_FORBIDDEN)


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
