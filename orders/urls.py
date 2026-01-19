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
    path("epaka/couriers/", views.epaka_couriers_view, name="epaka_couriers"),
    path("epaka/points/", views.epaka_points, name="epaka_points"),
    path("order/<int:pk>/", views.order_detail, name="order_detail"),
    path("pay/p24/start/<int:pk>/", views.p24_start, name="p24_start"),
    path("pay/p24/status/", views.p24_status, name="p24_status"),   # webhook

    path("cart/coupon/apply/", views.cart_apply_coupon, name="cart_apply_coupon"),
    path("cart/coupon/remove/", views.cart_remove_coupon, name="cart_remove_coupon"),

]