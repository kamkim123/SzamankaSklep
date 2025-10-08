from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .forms import SignupForm, EmailAuthenticationForm
from .models import Favorite
from products.models import Product


def home(request):
    return render(request, "home.html")

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data["password1"]
            auth_user = authenticate(request, username=user.get_username(), password=raw_password)
            if auth_user:
                login(request, auth_user)
                return redirect("home")  # lub 'users:user_panel'
            return render(request, "users/register.html", {"form": form, "auth_error": "Konto utworzone, ale nie udało się zalogować."})
        return render(request, "users/register.html", {"form": form})
    return render(request, "users/register.html", {"form": SignupForm()})


@login_required
def favorites_list(request):
    # Pobierz wszystkie produkty dodane do ulubionych przez użytkownika
    favs = Favorite.objects.select_related("product").filter(user=request.user)

    # Jeśli nie ma ulubionych produktów, wyświetl odpowiedni komunikat w szablonie
    if not favs.exists():
        empty = True
    else:
        empty = False

    return render(request, "users/favorites.html", {"favorites": favs, "empty": empty})


@login_required
def favorite_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Sprawdzenie, czy produkt jest już w ulubionych
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        fav.delete()  # Jeśli produkt już jest w ulubionych, usuwamy go

    return redirect(request.META.get("HTTP_REFERER") or "users:favorites")  # Powrót do poprzedniej strony


@login_required
def user_panel(request):
    orders = getattr(getattr(request.user, "orders", None), "all", lambda: [])()
    favorites = Favorite.objects.select_related("product").filter(user=request.user)
    addresses = getattr(getattr(getattr(request.user, "profile", None), "addresses", None), "all", lambda: [])()
    return render(request, "users/user-panel.html", {
        "orders": orders,
        "favorites": favorites,
        "addresses": addresses,
    })

from django.contrib.auth.views import LoginView

class EmailLoginView(LoginView):
    form_class = EmailAuthenticationForm
    template_name = "users/login.html"

    def form_valid(self, form):
        remember = self.request.POST.get("remember")
        # Domyślnie sesja wygaśnie po zamknięciu przeglądarki.
        # Jeśli zaznaczono remember -> ustaw czas życia np. 2 tygodnie.
        if remember:
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            self.request.session.set_expiry(0)  # do zamknięcia przeglądarki
        return super().form_valid(form)
