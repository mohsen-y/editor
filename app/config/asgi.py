"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault(key="DJANGO_SETTINGS_MODULE", value="config.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    application_mapping={
        "http": django_asgi_app,
    }
)
