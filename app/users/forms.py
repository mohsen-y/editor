from django.contrib.auth.forms import UserCreationForm as DefaultUserCreationForm
from users import models

class UserCreationForm(DefaultUserCreationForm):
    class Meta(DefaultUserCreationForm.Meta):
        model = models.User
