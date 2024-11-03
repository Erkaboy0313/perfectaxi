from django.urls import re_path

from .consumer import AdminConsumer

websocket_admin_urlpatterns = [
    re_path(r'ws/admin/', AdminConsumer.as_asgi()),
]