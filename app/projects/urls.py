from django.contrib.auth.decorators import login_required
from django.urls import path
from projects import views

urlpatterns = [
    path(
        route="projects/",
        view=login_required(function=views.projects_retrieve_project_create),
        name="projects_retrieve_project_create",
    ),
    path(
        route="projects/<uuid:project_pk>/",
        view=login_required(function=views.project_retrieve_file_create),
        name="project_retrieve_file_create",
    ),
]
