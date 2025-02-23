from rest_framework.serializers import Serializer,ModelSerializer
from parler_rest.serializers import TranslatableModelSerializer
from .models import AppLinks,Service,Pricing,Statistic,Review,DriverRequest


class PricingSerializer(TranslatableModelSerializer):
    class Meta:
        model = Pricing
        fields = "__all__"
        
class StatisticSerializer(TranslatableModelSerializer):
    class Meta:
        model = Statistic
        fields = "__all__"
        
class ServiceSerializer(TranslatableModelSerializer):
    prices = PricingSerializer(many = True)
    class Meta:
        model = Service
        fields = "__all__"
        
class AppLinksSeriazer(ModelSerializer):
    class Meta:
        model = AppLinks
        fields = "__all__"

class ReviewSeriazer(ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

class DriverRequestSeriazer(ModelSerializer):
    class Meta:
        model = DriverRequest
        fields = "__all__"

