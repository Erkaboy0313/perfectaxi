from rest_framework.viewsets import ModelViewSet,ViewSet
from .models import AppLinks,Service,Pricing,Statistic,Review,DriverRequest
from .serializers import PricingSerializer,StatisticSerializer,ServiceSerializer,AppLinksSeriazer,ReviewSeriazer,DriverRequestSeriazer



class AppLinksView(ModelViewSet):
    queryset  = AppLinks.objects.all()
    serializer_class = AppLinksSeriazer
    http_method_names = ['get']

class ServiceView(ModelViewSet):
    queryset  = Service.objects.all()
    serializer_class = ServiceSerializer
    http_method_names = ['get']

class PricingView(ModelViewSet):
    queryset  = Pricing.objects.all()
    serializer_class = PricingSerializer
    http_method_names = ['get']

class StatisticView(ModelViewSet):
    queryset  = Statistic.objects.all()
    serializer_class = StatisticSerializer
    http_method_names = ['get']

class ReviewView(ModelViewSet):
    queryset  = Review.objects.all()
    serializer_class = ReviewSeriazer
    http_method_names = ['get']

class DriverRequestView(ModelViewSet):
    queryset  = DriverRequest.objects.all()
    serializer_class = DriverRequestSeriazer
    http_method_names = ['get',"post"]