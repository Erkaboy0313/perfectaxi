from django.urls import re_path

from .async_consumer import OrderConsumer
from chat.consumer import ChatConsumer
from dashboard.route import websocket_admin_urlpatterns

websocket_urlpatterns = [
    re_path(r'ws/order/(?P<room_name>\w+)/$', OrderConsumer.as_asgi()),
    # re_path(r'ws/location/', consumer.LocationConsumer.as_asgi()),
    re_path(r'ws/chat/', ChatConsumer.as_asgi()),
]

websocket_urlpatterns.extend(websocket_admin_urlpatterns)