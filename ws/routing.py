from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<room_name>\w+)/$', consumer.OrderConsumer.as_asgi()),
    re_path(r'ws/location/', consumer.LocationConsumer.as_asgi())
]