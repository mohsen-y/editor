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
    path(
        route="projects/<uuid:project_pk>/destroy/",
        view=login_required(function=views.project_destroy),
        name="project_destroy",
    ),
    path(
        route="projects/<uuid:project_pk>/collaborations/",
        view=login_required(function=views.project_collaboration_create),
        name="project_collaboration_create",
    ),
    path(
        route="projects/<uuid:project_pk>/collaborations/destroy/",
        view=login_required(function=views.project_collaboration_destroy),
        name="project_collaboration_destroy",
    ),
    path(
        route="files/<uuid:file_pk>/",
        view=login_required(function=views.file_retrieve),
        name="file_retrieve",
    ),
    path(
        route="files/<uuid:file_pk>/history/",
        view=login_required(function=views.file_history_retrieve),
        name="file_history_retrieve",
    ),
    path(
        route="files/<uuid:file_pk>/destroy/",
        view=login_required(function=views.file_destroy),
        name="file_destroy",
    ),
]
