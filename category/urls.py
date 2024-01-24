from rest_framework.routers import DefaultRouter
from .views import CarSeriviceView,SavedLocationView
app_name = 'category'
category_router = DefaultRouter()

category_router.register(r'carservises',CarSeriviceView,basename='carservises')
category_router.register(r'savedlocation',SavedLocationView,basename='savedlocation')

