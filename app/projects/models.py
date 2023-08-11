from users.models import User
from django.db import models
import uuid

class Project(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=150, blank=False, null=False)
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="projects", blank=False, null=False
    )
    collaborators = models.ManyToManyField(
        to=User, through="ProjectCollaboration", related_name="collaborated_projects", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def is_owner(self, user: User) -> bool:
        return user == self.owner

    def is_collaborator(self, user: User) -> bool:
        return user in self.collaborators.all()

    class Meta:
        db_table = "projects_projects"
        unique_together = ["name", "owner"]


class File(models.Model):
    class Extension(models.TextChoices):  # TODO: add other types
        CSS = "css"
        PHP = "php"
        SQL = "sql"
        XML = "xml"
        HTML = "htmlmixed"
        CLIKE = "clike"
        PYTHON = "python"
        JAVASCRIPT = "javascript"
        UNKNOWN = "unknown"

    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=150, blank=False, null=False)
    extension = models.CharField(
        max_length=10, choices=Extension.choices, default=Extension.UNKNOWN, blank=False, null=False
    )
    project = models.ForeignKey(
        to=Project, on_delete=models.CASCADE, related_name="files", blank=False, null=False
    )
    creator = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name="files", blank=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects_files"
        unique_together = ["name", "project"]


class ProjectCollaboration(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="project_collaborations")
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="project_collaborations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects_project_collaborations"
        unique_together = ["user", "project"]


class FileConsumer(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, editable=False, default=uuid.uuid4)
    shadow = models.JSONField(blank=True, null=False)
    backup_shadow = models.JSONField(blank=True, null=False)

    class Meta:
        db_table = "projects_file_consumers"
