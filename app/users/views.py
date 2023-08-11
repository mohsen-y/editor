from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from django.conf import settings
from users import forms
import os

@require_http_methods(request_method_list=["GET", "POST"])
def user_create(request: HttpRequest):
    if request.user.is_authenticated:
        redirect_to = request.GET.get(
            REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL
        )
        return redirect(to=redirect_to)

    if request.method == "GET":
        return render(
            request=request,
            template_name=os.path.join("auth", "sign-up.html"),
        )

    elif request.method == "POST":
        form = forms.UserCreationForm(data=request.POST)

        if form.is_valid():
            user = form.save()
            login(request=request, user=user)
            redirect_to = request.GET.get(
                REDIRECT_FIELD_NAME, settings.LOGIN_REDIRECT_URL
            )
            return redirect(to=redirect_to)

        return render(
            request=request,
            template_name=os.path.join("auth", "sign-up.html"),
            context={"form": form},
        )
