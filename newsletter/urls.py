from django.urls import path
from .views import signup

app_name = "newsletter"

urlpatterns = [
    path("signup/", signup, name="signup"),
]
