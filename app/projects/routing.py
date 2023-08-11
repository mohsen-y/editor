from projects import consumers
from django.urls import path

websocket_urlpatterns = [
    path(
        route="ws/files/<uuid:file_pk>/file_consumers/<uuid:file_consumer_pk>/",
        view=consumers.FileConsumer.as_asgi(),
    ),
]
