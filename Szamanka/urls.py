from django.contrib import admin
from django.urls import path, include

from django.views.generic import TemplateView


urlpatterns = [

    path("", TemplateView.as_view(template_name="products/index.html"), name="home"),
    path("admin/", admin.site.urls),
    path("", include(("orders.urls", "orders"), namespace="orders")),
    path("u/", include(("users.urls", "users"), namespace="users")),
    path("products/", include(("products.urls", "products"), namespace="products")),
]
