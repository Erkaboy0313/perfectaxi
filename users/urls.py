from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from category.urls import category_router
from order.views import ServicesView,ClientOrderHistoryViewSet,DriverOrderHistoryViewSet,RejectReasonView,DriverWeeklyReportView,LastDestinationsViewSet
from creditCard.views import CardView
from payment.views import ChangePaymentMethodView,BalanceView
from feedback.views import FeedBackView,ReasonView
from ws.views import CalculatePrice

app_name = 'users'
router = DefaultRouter()

# user auth views
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'driver',views.DriverViewSet, basename='driver')
router.register(r'client',views.ClientViewSet, basename='client')
router.register(r'available-service',views.DriverAvailabelServiceView, basename='available-service')

# credit card views
router.register(r'card',CardView, basename='card')

# payment views
router.register(r'payment_type',ChangePaymentMethodView, basename='payment_type')
router.register(r'balance',BalanceView, basename='balance')

# feedback views
router.register(r'feedback',FeedBackView, basename='feedback')
router.register(r'reason',ReasonView, basename='reason')

# order views
router.register(r'serivice',ServicesView, basename='serivice')
router.register(r'client-order-history',ClientOrderHistoryViewSet, basename='client-history')
router.register(r'driver-order-history',DriverOrderHistoryViewSet, basename='driver-history')
router.register(r'reject-reason',RejectReasonView, basename='reject-reason')
router.register(r'weekly-report',DriverWeeklyReportView, basename='weekly-report')
router.register(r'last-point',LastDestinationsViewSet, basename='last-point')

urlpatterns = [
    path('api/v1/calculate-price/', CalculatePrice.as_view(), name='calculate-price'),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(category_router.urls)),
]
