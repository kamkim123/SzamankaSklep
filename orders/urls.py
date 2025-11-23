from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("thank-you/<int:pk>/", views.thank_you, name="thank_you"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/update/", views.cart_update_qty, name="cart_update"),

    path("epaka/label/<int:pk>/", views.epaka_label_view, name="epaka_label"),
]