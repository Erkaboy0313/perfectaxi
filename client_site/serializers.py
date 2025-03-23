from rest_framework.serializers import Serializer,ModelSerializer
from parler_rest.serializers import TranslatableModelSerializer,TranslatedFieldsField
from .models import AppLinks,Service,Pricing,Statistic,Review,DriverRequest,ContactUs


class PricingSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Pricing)

    class Meta:
        model = Pricing
        fields = "__all__"
        
class StatisticSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Statistic)

    class Meta:
        model = Statistic
        fields = "__all__"
        
class ServiceSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Service)

    prices = PricingSerializer(many = True)
    class Meta:
        model = Service
        fields = "__all__"
        
class ContactUsSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=ContactUs)

    class Meta:
        model = ContactUs
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

