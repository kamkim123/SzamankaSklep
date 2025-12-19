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

import base64
from django.http import JsonResponse

from decimal import Decimal

DEFAULT_PRICE = Decimal("999.99")

DEFAULT_IMAGE = "static/products/images/default-image.png"

def only_with_price_and_image(qs):
    return (
        qs.exclude(price=DEFAULT_PRICE)
          .exclude(product_image__isnull=True)
          .exclude(product_image="")
          .exclude(product_image=DEFAULT_IMAGE)
    )

# views.py

# views.py

class IndexView(generic.ListView):
    model = Product
    template_name = "products/index.html"  # Główna strona
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        qs = only_with_price_and_image(Product.objects.all()).order_by("-id")
  # Pobieramy wszystkie produkty posortowane według ID

        selected = (self.request.GET.get("type") or "").strip()

        if selected:
            qs = qs.filter(product_type=selected)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected = (self.request.GET.get("type") or "").strip()

        # Dodajemy listę kategorii
        ctx["categories"] = (
            only_with_price_and_image(Product.objects.all())
            .values("product_type")
            .annotate(count=Count("id"))
            .order_by("-product_type")
        )

        # Pobieramy bestsellery i dodajemy do kontekstu
        bestsellers = only_with_price_and_image(Product.objects.filter(is_bestseller=True))

        ctx["bestsellers"] = bestsellers

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
        similar_products = (
            only_with_price_and_image(Product.objects.filter(is_bestseller=True))
            .exclude(pk=product.pk)
        )
        # Wykluczamy obecny produkt
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
        qs = only_with_price_and_image(Product.objects.all())


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
            only_with_price_and_image(Product.objects.all())
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

        qs = only_with_price_and_image(Product.objects.all())

        if q:
            qs = qs.filter(Q(product_name__icontains=q))
        qs = qs.order_by("product_name")[:limit]

        data = [{"product_name": p.product_name} for p in qs]

        return JsonResponse({"results": data})


def produkty(request):
    product_type = request.GET.get('type', 'all')
    if product_type == 'all':
        produkty = only_with_price_and_image(Product.objects.all())

    else:
        produkty = only_with_price_and_image(Product.objects.filter(product_type=product_type))


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
    query = request.GET.get('q', '')
    if query:
        products = only_with_price_and_image(
            Product.objects.filter(product_name__icontains=query)
        )

        results = [{'id': product.id, 'product_name': product.product_name} for product in products]
    else:
        results = []
    return JsonResponse({'results': results})




from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

def search_results(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    res = None
    game = request.POST.get('game', '')
    qs = only_with_price_and_image(
        Product.objects.filter(product_name__icontains=game)
    )[:10]

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

# views.py


def epaka_login(request):
    params = {
        "response_type": "code",
        "client_id": settings.EPAKA_CLIENT_ID,
        "redirect_uri": settings.EPAKA_REDIRECT_URI,
        "scope": "api",  # zgodnie z dokumentacją – domyślnie 'api'
        # opcjonalnie:
        # "state": "losowy_token_do_csrf",
        # "code_challenge_method": "S256",
        # "code_challenge": "...",
    }
    url = f"{settings.EPAKA_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    return redirect(url)

# views.py


def epaka_callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponseBadRequest("Brak parametru 'code'")

    # body x-www-form-urlencoded
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.EPAKA_REDIRECT_URI,
    }

    # Authorization: Basic base64(client_id:client_secret)
    auth_raw = f"{settings.EPAKA_CLIENT_ID}:{settings.EPAKA_CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_raw.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    resp = requests.post(settings.EPAKA_TOKEN_URL, data=data, headers=headers)
    if resp.status_code != 200 and resp.status_code != 201:
        return HttpResponseBadRequest(f"Błąd tokenu: {resp.status_code} {resp.text}")

    token_data = resp.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not access_token:
        return HttpResponseBadRequest(f"Brak access_token w odpowiedzi: {token_data}")

    # na razie do sesji (później możesz przenieść do bazy powiązanej z userem)
    request.session["epaka_access_token"] = access_token
    request.session["epaka_refresh_token"] = refresh_token

    return redirect("epaka_profile")



# np. w tym samym pliku views.py lub w osobnym services.py

def epaka_api_get(endpoint, access_token, params=None):
    url = settings.EPAKA_API_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",  # 👈 to jest klucz
    }
    resp = requests.get(url, headers=headers, params=params or {})
    return resp


def epaka_profile_view(request):
    access_token = request.session.get("epaka_access_token")
    if not access_token:
        return redirect("epaka_login")

    resp = epaka_api_get("/v1/user", access_token)

    if resp.status_code == 403:
        return HttpResponseBadRequest("Brak autoryzacji w Epaka API")

    if resp.status_code != 200:
        return HttpResponseBadRequest(f"Błąd: {resp.status_code} {resp.text}")

    data = resp.json()
    return render(request, "products/epaka_profile.html", {"profile": data})


def epaka_api_post(endpoint, access_token, payload):
    url = settings.EPAKA_API_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp


