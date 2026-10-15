
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from conversations.middleware import JWTAuthMiddleware
from conversations.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})

