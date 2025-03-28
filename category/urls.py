from rest_framework.routers import DefaultRouter
from .views import CarSeriviceView,SavedLocationView,CarBrendViewSet,ColorViewSet,CarModelViewSet
app_name = 'category'
category_router = DefaultRouter()

category_router.register(r'carmodel',CarModelViewSet,basename='carmodel')
category_router.register(r'color',ColorViewSet,basename='color')
category_router.register(r'carbrand',CarBrendViewSet,basename='carbrand')
category_router.register(r'carservises',CarSeriviceView,basename='carservises')
category_router.register(r'savedlocation',SavedLocationView,basename='savedlocation')

