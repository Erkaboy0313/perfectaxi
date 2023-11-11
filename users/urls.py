from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from category.urls import category_router
from order.views import ServicesView,OrderHistoryView
from creditCard.views import CardView
from payment.views import ChangePaymentMethodView,BalanceView
from feedback.views import FeedBackView

app_name = 'users'
router = DefaultRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'driver',views.DriverViewSet, basename='driver')
router.register(r'client',views.ClientViewSet, basename='client')
router.register(r'serivice',ServicesView, basename='serivice')
router.register(r'orderhistory',OrderHistoryView, basename='history')
router.register(r'card',CardView, basename='card')
router.register(r'payment_type',ChangePaymentMethodView, basename='payment_type')
router.register(r'balance',BalanceView, basename='balance')
router.register(r'feedback',FeedBackView, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
