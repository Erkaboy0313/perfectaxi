from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from category.urls import category_router
from order.views import ServicesView,OrderHistoryView,RejectReasonView,DriverWeeklyReportView,LastDestinationsViewSet
from creditCard.views import CardView
from payment.views import ChangePaymentMethodView,BalanceView
from feedback.views import FeedBackView,ReasonView

app_name = 'users'
router = DefaultRouter()

router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'driver',views.DriverViewSet, basename='driver')
router.register(r'client',views.ClientViewSet, basename='client')
router.register(r'available-service',views.DriverAvailabelServiceView, basename='available-service')
router.register(r'serivice',ServicesView, basename='serivice')
router.register(r'orderhistory',OrderHistoryView, basename='history')
router.register(r'card',CardView, basename='card')
router.register(r'payment_type',ChangePaymentMethodView, basename='payment_type')
router.register(r'balance',BalanceView, basename='balance')
router.register(r'feedback',FeedBackView, basename='feedback')
router.register(r'reason',ReasonView, basename='reason')
router.register(r'reject-reason',RejectReasonView, basename='reject-reason')
router.register(r'weekly-report',DriverWeeklyReportView, basename='weekly-report')
router.register(r'last-point',LastDestinationsViewSet, basename='last-point')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
]
