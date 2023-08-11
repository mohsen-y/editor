from django.contrib.auth import views as auth_views
from users import views as users_views
from django.urls import path
import os

urlpatterns = [
    path(
        route="users/sign-up/",
        view=users_views.user_create,
        name="user_create",
    ),
    path(
        route="users/sign-in/",
        view=auth_views.LoginView.as_view(
            template_name=os.path.join("auth", "sign-in.html"),
            redirect_authenticated_user=True,
        ),
        name="user_sign_in",
    ),
    path(
        route="users/sign-out/",
        view=auth_views.LogoutView.as_view(),
        name="user_sign_out",
    ),
]
