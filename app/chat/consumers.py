from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer
from projects.models import File
from chat.models import Message
from typing import Dict
import json

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_layer: RedisChannelLayer

    async def connect(self):
        file_pk = self.scope["url_route"]["kwargs"]["file_pk"]

        self.file = await File.objects.filter(pk=file_pk).afirst()  # TODO: grant chat access

        if not self.file:
            await self.close()
            return

        await self.channel_layer.group_add(group=str(file_pk), channel=self.channel_name)
        await self.accept()

    async def disconnect(self, code: int):
        await self.channel_layer.group_discard(group=str(self.file.pk), channel=self.channel_name)

    async def receive(self, text_data: str = None, bytes_data: bytes = None):
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message_content"]

        message = await Message.objects.acreate(
            content=message_content, file=self.file, creator=self.scope["user"]
        )
        message = {
            "content": message.content,
            "creator": {"username": message.creator.username},
            "created_at": str(message.created_at),
        }

        await self.channel_layer.group_send(
            group=str(self.file.pk),
            message={"type": "chat.message", "message": message},
        )

    async def chat_message(self, event: Dict):
        await self.send(text_data=json.dumps({"message": event["message"]}))
