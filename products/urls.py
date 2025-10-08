# products/urls.py
from django.urls import path
from . import views
from .views import ProductListView

app_name = "products"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),          # /products/ => IndexView
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),  # szczegóły produktu
    path('produkty/', views.produkty, name='produkty'),
    path('products/', ProductListView.as_view(), name='produkty'),# Dodaj ścieżkę do funkcji `produkty`
]


