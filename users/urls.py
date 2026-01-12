# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailAuthenticationForm

app_name = "users"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("register/", views.signup, name="register"),
    path("signup/email-sent/", views.signup_email_sent, name="signup_email_sent"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("user-panel/", views.user_panel, name="user-panel"),
    path("favorites/", views.favorites_list, name="favorites"),  # Strona z ulubionymi produktami
    path("favorite/<int:product_id>/toggle/", views.favorite_toggle, name="favorite_toggle"),
    path("activate/<str:uidb64>/<str:token>/", views.activate, name="activate"),
    # Dodanie/Usunięcie z ulubionych

    path("panel/profile/edit/", views.edit_profile, name="edit_profile"),
    path("panel/address/add/", views.add_address, name="add_address"),
    path("panel/address/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("panel/address/<int:pk>/delete/", views.delete_address, name="delete_address"),

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.txt",
            subject_template_name="users/password_reset_subject.txt",
            success_url="/u/password-reset/done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url="/u/reset/done/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),

]


from django.contrib.auth import views as auth_views

urlpatterns += [
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.txt",
            subject_template_name="users/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

