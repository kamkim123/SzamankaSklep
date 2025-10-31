# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import EmailAuthenticationForm

app_name = "users"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("register/", views.signup, name="register"),
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

]

