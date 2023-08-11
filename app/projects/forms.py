from django.core.exceptions import NON_FIELD_ERRORS
from django.forms import ModelForm
from projects import models

class ProjectForm(ModelForm):
    class Meta:
        model = models.Project
        fields = ["name", "owner"]
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "%(model_name)s already exists.",
            },
        }


class FileForm(ModelForm):
    class Meta:
        model = models.File
        fields = ["name", "project", "creator"]
        error_messages = {
            NON_FIELD_ERRORS: {
                "unique_together": "%(model_name)s already exists.",
            },
            "name": {
                "required": "Enter file's name or choose an existing file.",
            },
        }
