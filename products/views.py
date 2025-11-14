from django.views import generic, View
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest
import requests
import urllib.parse


from users.models import Favorite
from .models import Product
from django.db.models import Count
from django.views.generic import ListView

from django.db.models import Q

# views.py

# views.py

class IndexView(generic.ListView):
    model = Product
    template_name = "products/index.html"  # Główna strona
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = Product.objects.order_by("-id")  # Pobieramy wszystkie produkty posortowane według ID
        selected = (self.request.GET.get("type") or "").strip()

        if selected:
            qs = qs.filter(product_type=selected)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected = (self.request.GET.get("type") or "").strip()

        # Dodajemy listę kategorii
        ctx["categories"] = Product.objects.values("product_type").annotate(count=Count("id")).order_by("-product_type")
        ctx["selected"] = selected

        # Pobieramy bestsellery i dodajemy do kontekstu
        bestsellers = Product.objects.filter(is_bestseller=True)
        ctx["bestsellers"] = bestsellers  # Dodajemy bestsellery do kontekstu

        if self.request.user.is_authenticated:
            favorite_product_ids = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            ctx["favorite_product_ids"] = favorite_product_ids

        return ctx


from django.views.generic import DetailView



class DetailView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.object  # Produkt, który jest oglądany

        # Dodanie podobnych produktów (bestsellerów)
        similar_products = Product.objects.filter(is_bestseller=True).exclude(pk=product.pk)  # Wykluczamy obecny produkt
        context['similar_products'] = similar_products

        # Dodajemy listę produktów w ulubionych, jeśli użytkownik jest zalogowany
        if self.request.user.is_authenticated:
            favorite_product_ids = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            context["favorite_product_ids"] = favorite_product_ids

        return context


# Jeśli naprawdę potrzebujesz ResultsView pod oddzielny template,
# zostawiam jako alias do szczegółów. Możesz też usunąć całkiem.
class ResultsView(generic.DetailView):
    model = Product
    template_name = "products/results.html"
    context_object_name = "product"

# views.py

class ProductListView(ListView):
    model = Product
    template_name = "products/products.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = Product.objects.all()

        # Jeśli parametr 'bestsellers' jest w URL, filtruj produkty, które są bestsellerami
        if 'bestsellers' in self.request.GET:
            qs = qs.filter(is_bestseller=True)

        if 'promocje' in self.request.GET:
            qs = qs.filter(is_promotion=True)

        if 'nowosci' in self.request.GET:
            qs = qs.filter(is_new=True)

        if 'najpopularniejsze' in self.request.GET:
            qs = qs.filter(is_popular=True)

        selected = (self.request.GET.get("type") or "").strip()
        if selected:
            qs = qs.filter(product_type=selected)

        return qs


    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected = self.request.GET.get("type", "").strip()
        ctx["selected"] = selected
        ctx["categories"] = (
            Product.objects
            .values("product_type")
            .annotate(count=Count("id"))
            .order_by("product_type")
        )

        if self.request.user.is_authenticated:
            favorite_product_ids = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
            ctx["favorite_product_ids"] = favorite_product_ids
        return ctx


class ProductSearchView(ProductListView):
    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(product_name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        return ctx

class ProductSearchAPI(View):
    def get(self, request):
        q = (request.GET.get("q") or "").strip()
        limit = int(request.GET.get("limit") or 10)

        qs = Product.objects.all()
        if q:
            qs = qs.filter(Q(product_name__icontains=q))
        qs = qs.order_by("product_name")[:limit]

        data = [{"product_name": p.product_name} for p in qs]

        return JsonResponse({"results": data})


def produkty(request):
    product_type = request.GET.get('type', 'all')  # Domyślnie 'all' w przypadku braku parametru
    if product_type == 'all':
        produkty = Product.objects.all()  # Wyświetlanie wszystkich produktów
    else:
        produkty = Product.objects.filter(product_type=product_type)  # Filtrujemy po typie

    return render(request, 'products/products.html', {'produkty': produkty, 'kategoria': product_type})



# products/views.py
from django.shortcuts import render

def regulamin(request):
    return render(request, "products/regulamin.html")


def private(request):  # Dodaj funkcję widoku dla polityki prywatności
    return render(request, "products/private.html")





from django.http import JsonResponse
from .models import Product

def search_products(request):
    query = request.GET.get('q', '')  # Pobieramy zapytanie 'q'
    if query:
        # Filtrujemy produkty na podstawie nazwy
        products = Product.objects.filter(product_name__icontains=query)
        results = [{'id': product.id, 'product_name': product.name} for product in products]
    else:
        results = []
    return JsonResponse({'results': results})



from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect


def search_results(request):
    # jeśli koniecznie chcesz sprawdzić „AJAX”:
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    res = None
    game = request.POST.get('game', '')
    qs = Product.objects.filter(product_name__icontains=game)[:10]

    if len(qs) > 0 and len(game) > 0:
        data = []
        for pos in qs:
            item = {
                'product_name': pos.product_name,
                'product_id': pos.id
            }
            data.append(item)
        res = data
    else:
        res = 'No products found'

    return JsonResponse({'data': res})



# views.py






