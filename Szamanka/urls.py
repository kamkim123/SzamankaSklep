from django.contrib import admin
from django.urls import path, include



from products import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("", include(("orders.urls", "orders"), namespace="orders")),
    path("u/", include(("users.urls", "users"), namespace="users")),
    path("accounts/", include("allauth.urls")),  # to dodaje ~30 endpointów allauth
    path("products/", include(("products.urls", "products"), namespace="products")),
]
