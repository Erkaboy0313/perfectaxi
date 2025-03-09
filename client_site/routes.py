from rest_framework import routers
from django.conf import settings
from django.urls import path,include
from .views import AppLinksView,ServiceView,PricingView,StatisticView,ReviewView,DriverRequestView

if settings.DEBUG:
    client_site = routers.DefaultRouter()
else:
    client_site = routers.SimpleRouter()

client_site.register(r'applink',AppLinksView,basename='applink')
client_site.register(r'service',ServiceView,basename='client-service')
client_site.register(r'price',PricingView,basename='price')
client_site.register(r'statistics',StatisticView,basename='statistics')
client_site.register(r'review',ReviewView,basename='review')
client_site.register(r'driver-request',DriverRequestView,basename='driver-request')
    
    
urlpatterns = [
    path('', include(client_site.urls)),
]
