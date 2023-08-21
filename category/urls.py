from rest_framework.routers import DefaultRouter
from .views import CarSeriviceView
from django.urls import path,include
app_name = 'category'
category_router = DefaultRouter()

category_router.register(r'carservises',CarSeriviceView,basename='carservises')

