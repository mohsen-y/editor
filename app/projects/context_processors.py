from django.http.request import HttpRequest
from django.db.models import Q
from projects import models
from typing import Dict

def projects(request: HttpRequest) -> Dict:
    context_extras = {}
    if request.user.is_authenticated:
        context_extras["projects"] = models.Project.objects.filter(owner=request.user).all()
        context_extras["project_collaborations"] = models.ProjectCollaboration.objects.filter(
            ~Q(project__owner=request.user), user=request.user
        ).all()
    return context_extras
