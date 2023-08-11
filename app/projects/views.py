from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from projects.utils import file_extensions
from chat import models as chat_models
from projects import forms, models
from django.conf import settings
import shutil
import os

@require_http_methods(request_method_list=["GET", "POST"])
def projects_retrieve_project_create(request: HttpRequest):
    if request.method == "GET":
        return render(
            request=request,
            template_name=os.path.join("projects", "retrieve-all.html"),
        )

    elif request.method == "POST":
        data = request.POST.copy()
        data.update({"owner": request.user.pk})

        form = forms.ProjectForm(data=data)

        if form.is_valid():
            project = form.save()
            project.collaborators.add(project.owner)
            project.save()
            os.mkdir(path=os.path.join(settings.MEDIAFILES_DIR, "projects", str(project.pk)))

            return redirect(
                to="project_retrieve_file_create",
                project_pk=project.pk,
            )

        return render(
            request=request,
            template_name=os.path.join("projects", "retrieve-all.html"),
            context={"form": form},
        )
