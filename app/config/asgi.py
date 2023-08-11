"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

from projects.routing import websocket_urlpatterns as projects_websocket_urlpatterns
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import os

websocket_urlpatterns = projects_websocket_urlpatterns

os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="config.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    application_mapping={
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            application=AuthMiddlewareStack(
                inner=URLRouter(routes=websocket_urlpatterns),
            ),
        ),
        "channel": ChannelNameRouter(
            application_mapping={},
        ),
    },
)
