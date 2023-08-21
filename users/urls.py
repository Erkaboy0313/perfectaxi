from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from category.urls import category_router
from order.views import ServicesView

app_name = 'users'
router = DefaultRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'driver',views.DriverViewSet, basename='driver')
router.register(r'client',views.ClientViewSet, basename='client')
router.register(r'serivice',ServicesView, basename='serivice')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
