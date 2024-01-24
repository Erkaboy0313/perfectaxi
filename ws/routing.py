from django.urls import re_path

from .async_consumer import OrderConsumer
from chat.consumer import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<room_name>\w+)/$', OrderConsumer.as_asgi()),
    # re_path(r'ws/location/', consumer.LocationConsumer.as_asgi()),
    re_path(r'ws/chat/', ChatConsumer.as_asgi()),
]