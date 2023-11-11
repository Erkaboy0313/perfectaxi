from rest_framework import viewsets,response,status
from .serializers import FeedbackSerializer,Feedback
from users.permissions import IsActive
from django.utils import timezone
from django.db.models import Avg


class FeedBackView(viewsets.ViewSet):
    permission_classes = (IsActive,)

    def create(self,request):
        if request.usre.role == 'client':
            serializer = FeedbackSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return response.Response({"error":"method not allowed"},status=status.HTTP_403_FORBIDDEN)

    def list(self,request):
        if request.user.role == 'driver':
            last_7_days = timezone.now() - timezone.timedelta(days=7)
            rate = Feedback.objects.filter(driver__user = request.user,time__gte = last_7_days).aggregate(average = Avg('mark'))
            return response.Response({"mark":rate['average']},status=status.HTTP_200_OK)
        else:
            return response.Response({"error":"method not allowed"},status=status.HTTP_403_FORBIDDEN)
