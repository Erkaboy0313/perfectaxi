from rest_framework import serializers
from .models import Feedback,Reson


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class ResonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reson
        fields = '__all__'
