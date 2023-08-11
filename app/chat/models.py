from projects.models import File
from users.models import User
from django.db import models
import uuid

class Message(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)
    content = models.CharField(max_length=250, blank=False, null=False)
    file = models.ForeignKey(
        to=File, on_delete=models.CASCADE, related_name="messages", blank=False, null=False
    )
    creator = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="messages", blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "chat_messages"
