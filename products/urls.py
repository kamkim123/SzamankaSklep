# products/urls.py
from django.urls import path, include
from . import views
from .views import ProductListView, ProductSearchView, ProductSearchAPI, search_results

app_name = "products"
urlpatterns = [
    path("", views.ProductListView.as_view(), name="index"),          # /products/ => IndexView
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),  # szczegóły produktu
    path('produkty/', views.produkty, name='produkty'),
    path('products/', ProductListView.as_view(), name='produkty'),# Dodaj ścieżkę do funkcji `produkty`
    path("regulamin/", views.regulamin, name="regulamin"),
    path("polityka-prywatnosci/", views.private, name="private"),  # Ścieżka do polityki prywatności
    path("search/", ProductSearchView.as_view(), name="search_products"),
    path("api/szukaj", ProductSearchAPI.as_view(), name="product_search_api"),
    path("search2/", search_results, name="search2"),
]


