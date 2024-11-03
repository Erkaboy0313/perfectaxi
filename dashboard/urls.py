from rest_framework.routers import DefaultRouter
dashboard = DefaultRouter()
from django.urls import path,include

from .views import DriverViewset,ClientViewSet,OrderViewSet,BalanceViewSet,PaymentViewSet,CarBrendViewSet,ColorViewSet,AdminLoginViewSet
from category.views import CarSeriviceView

dashboard.register(r'login', AdminLoginViewSet, basename='login')
dashboard.register(r'driver', DriverViewset, basename='driver')
dashboard.register(r'client', ClientViewSet, basename='client')
dashboard.register(r'order', OrderViewSet, basename='order')
dashboard.register(r'service', CarSeriviceView, basename='service')
dashboard.register(r'balance', BalanceViewSet, basename='balance')
dashboard.register(r'payment', PaymentViewSet, basename='payment')
dashboard.register(r'car-barnd', CarBrendViewSet, basename='car-barnd')
dashboard.register(r'color', ColorViewSet, basename='color')


urlpatterns = [
    path('', include(dashboard.urls)),
]
