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

    project.delete()  # TODO: notify users working on the porject (and its files)

    return redirect(to="projects_retrieve_project_create")


@require_http_methods(request_method_list=["GET", "POST"])
def project_collaboration_create(request: HttpRequest, project_pk: int):
    if request.method == "GET":
        project = models.Project.objects.filter(pk=project_pk).first()
        if not project: return render(request=request, template_name="404.html")

        if project.is_owner(user=request.user) or project.is_collaborator(user=request.user):
            return redirect(
                to="project_retrieve_file_create",
                project_pk=project_pk,
            )

        return render(
            request=request,
            template_name=os.path.join("projects", "collaborations", "create.html"),
            context={"project": project,}
        )

    elif request.method == "POST":
        project = models.Project.objects.filter(pk=project_pk).first()
        if not project: return render(request=request, template_name="404.html")

        project.collaborators.add(request.user)
        project.save()

        return redirect(
            to="project_retrieve_file_create",
            project_pk=project_pk,
        )


@require_http_methods(request_method_list=["POST"])
def project_collaboration_destroy(request: HttpRequest, project_pk: int):
    project = models.Project.objects.filter(pk=project_pk).first()
    if not project: return render(request=request, template_name="404.html")

    project.collaborators.remove(request.user)
    project.save()

    redirect_to = request.META.get("HTTP_REFERER", "project_collaboration_create")

    return redirect(
        to=redirect_to,
        project_pk=project.pk,
    )


@require_http_methods(request_method_list=["GET"])
def file_retrieve(request: HttpRequest, file_pk: int):
    file = models.File.objects.filter(pk=file_pk).first()
    if not file: return render(request=request, template_name="404.html")
    is_project_owner = file.project.is_owner(user=request.user)

    if not is_project_owner:
        is_project_collaborator = file.project.is_collaborator(user=request.user)
        if not is_project_collaborator:
            return redirect(
                to="project_collaboration_create",
                project_pk=file.project.pk,
            )

    with open(
        file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(file.project.pk), str(file.pk)), mode="r"
    ) as patch_file: file_content = patch_file.read()

    file_consumer = models.FileConsumer.objects.create(
        shadow={
            "content": file_content,
            "client_version": 0,
            "server_version": 0,
        },
        backup_shadow={
            "content": file_content,
            "server_version": 0,
        },
    )

    chat_messages = chat_models.Message.objects.filter(file=file).order_by("created_at").all()

    return render(
        request=request,
        template_name=os.path.join("files", "retrieve.html"),
        context={
            "file": file,
            "file_content": file_content,
            "file_consumer_pk": file_consumer.pk,
            "is_project_owner": is_project_owner,
            "chat_messages": chat_messages,
        },
    )


@require_http_methods(request_method_list=["GET"])
def file_history_retrieve(request: HttpRequest, file_pk: int):
    file = models.File.objects.filter(pk=file_pk).first()
    if not file: return render(request=request, template_name="404.html")
    is_project_owner = file.project.is_owner(user=request.user)

    if not is_project_owner:
        is_project_collaborator = file.project.is_collaborator(user=request.user)
        if not is_project_collaborator:
            return redirect(
                to="project_collaboration_create",
                project_pk=file.project.pk,
            )

    with open(
        file=os.path.join(settings.MEDIAFILES_DIR, "projects", str(file.project.pk), f"{file.pk}.patch"), mode="r"
    ) as patch_file: patch_file_content = patch_file.read()

    return render(
        request=request,
        template_name=os.path.join("files", "retrieve-history.html"),
        context={
            "file": file,
            "patch_file_content": patch_file_content,
            "is_project_owner": is_project_owner,
        },
    )


@require_http_methods(request_method_list=["POST"])
def file_destroy(request: HttpRequest, file_pk: int):
    file = models.File.objects.filter(pk=file_pk).first()
    if not file: return render(request=request, template_name="404.html")

    # TODO: database transaction
    os.remove(path=os.path.join(settings.MEDIAFILES_DIR, "projects", str(file.project.pk), str(file.pk)))
    os.remove(path=os.path.join(settings.MEDIAFILES_DIR, "projects", str(file.project.pk), f"{file.pk}.patch"))

    file.delete()  # TODO: notify users working on the file

    return redirect(
        to="project_retrieve_file_create",
        project_pk=file.project.pk,
    )
