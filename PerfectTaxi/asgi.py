import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PerfectTaxi.settings')
django.setup()

from utils.wsauthentication import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

import ws.routing

application = ProtocolTypeRouter({
  "http": django_asgi_app,
    "websocket":AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                ws.routing.websocket_urlpatterns,
            )
        ),
    ),
})