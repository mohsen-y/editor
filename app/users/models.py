from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)

    class Meta:
        db_table = "users_users"
