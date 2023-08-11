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


@require_http_methods(request_method_list=["GET", "POST"])
def project_retrieve_file_create(request: HttpRequest, project_pk: int):
    if request.method == "GET":
        project = models.Project.objects.filter(pk=project_pk).first()
        if not project: return render(request=request, template_name="404.html")
        is_project_owner = project.is_owner(user=request.user)

        if not is_project_owner:
            is_project_collaborator = project.is_collaborator(user=request.user)
            if not is_project_collaborator:
                return redirect(
                    to="project_collaboration_create",
                    project_pk=project_pk,
                )

        return render(
            request=request,
            template_name=os.path.join("projects", "retrieve.html"),
            context={
                "project": project,
                "is_project_owner": is_project_owner,
            },
        )

    elif request.method == "POST":
        project = models.Project.objects.filter(pk=project_pk).first()
        if not project: return render(request=request, template_name="404.html")
        is_project_owner = project.is_owner(user=request.user)

        data = request.POST.copy()
        data.update({"project": project.pk, "creator": request.user.pk})

        uploaded_file = request.FILES.get("file", None)
        if uploaded_file: data.update({"name": uploaded_file.name})  # TODO: validate file's name and size and extension

        form = forms.FileForm(data=data)

        if form.is_valid():
            file = form.save(commit=False)

            _, file_extension = os.path.splitext(form.cleaned_data["name"])

            if file_extension.lower() in file_extensions.CSS_EXTENSIONS:
                file.extension = models.File.Extension.CSS
            elif file_extension.lower() in file_extensions.PHP_EXTENSIONS:
                file.extension = models.File.Extension.PHP
            elif file_extension.lower() in file_extensions.SQL_EXTENSIONS:
                file.extension = models.File.Extension.SQL
            elif file_extension.lower() in file_extensions.XML_EXTENSIONS:
                file.extension = models.File.Extension.XML
            elif file_extension.lower() in file_extensions.HTML_EXTENSIONS:
                file.extension = models.File.Extension.HTML
            elif file_extension.lower() in file_extensions.CLIKE_EXTENSIONS:
                file.extension = models.File.Extension.CLIKE
            elif file_extension.lower() in file_extensions.PYTHON_EXTENSIONS:
                file.extension = models.File.Extension.PYTHON
            elif file_extension.lower() in file_extensions.JAVASCRIPT_EXTENSIONS:
                file.extension = models.File.Extension.JAVASCRIPT
            else: file.extension = models.File.Extension.UNKNOWN

            file.save()

            with open(
                file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(project_pk), str(file.pk)), mode="wb"
            ) as created_file:
                if uploaded_file: created_file.write(uploaded_file.read())

            with open(
                file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(project_pk), f"{file.pk}.patch"), mode="w"
            ): pass

        return render(
            request=request,
            template_name=os.path.join("projects", "retrieve.html"),
            context={
                "project": project,
                "is_project_owner": is_project_owner,
                "form": form,
            },
        )


@require_http_methods(request_method_list=["POST"])
def project_destroy(request: HttpRequest, project_pk: int):
    project = models.Project.objects.filter(pk=project_pk).first()
    if not project: return render(request=request, template_name="404.html")

    # TODO: database transaction
    shutil.rmtree(path=os.path.join(settings.MEDIAFILES_DIR, "projects", str(project.pk)))

    project.delete()

    return redirect(to="projects_retrieve_project_create")
