from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'
router = DefaultRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'driver',views.DriverViewSet, basename='driver')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
