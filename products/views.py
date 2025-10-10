from django.views import generic
from django.shortcuts import render
from .models import Product
from django.db.models import Count
from django.views.generic import ListView

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

        return ctx


class DetailView(generic.DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"


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
        return ctx



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

