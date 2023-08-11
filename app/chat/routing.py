from django.urls import path
from chat import consumers

websocket_urlpatterns = [
    path(
        route="ws/files/<uuid:file_pk>/chat/",
        view=consumers.ChatConsumer.as_asgi(),
    ),
]
