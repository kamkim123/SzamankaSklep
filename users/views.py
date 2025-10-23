from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .forms import SignupForm, EmailAuthenticationForm
from .models import Favorite, Profile
from products.models import Product
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect


def home(request):
    return render(request, "home.html")


def send_activation_email(user, request):
    token = default_token_generator.make_token(user)  # Tworzymy token
    uid = urlsafe_base64_encode(str(user.pk).encode()).decode()  # Kodujemy ID użytkownika

    domain = get_current_site(request).domain
    link = f"http://{domain}/activate/{uid}/{token}/"  # Tworzymy link do aktywacji

    message = render_to_string('users/activation_email.html', {
        'user': user,
        'activation_link': link,
    })

    send_mail(
        'Aktywacja konta',
        message,
        'noreply@example.com',  # Adres nadawcy
        [user.email],
    )


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Aktywuj konto użytkownika
        user.profile.is_active = True
        user.profile.save()
        messages.success(request, "Twoje konto zostało aktywowane!")
        return redirect("users:login")  # Przekierowanie na stronę logowania
    else:
        messages.error(request, "Link aktywacyjny jest nieprawidłowy lub wygasł.")
        return redirect("home")  # Przekierowanie na stronę główną


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tworzymy profil użytkownika, ustawiamy, że konto nie jest aktywowane
            profile = Profile.objects.create(user=user)

            # Tworzymy użytkownika i wysyłamy link aktywacyjny
            send_activation_email(user, request)

            # Możesz przekierować użytkownika na stronę logowania lub informacyjną
            return render(request, "users/register.html",
                          {"form": form, "info": "Zarejestrowano! Sprawdź swoją pocztę e-mail w celu aktywacji konta."})

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


from django.http import JsonResponse

@login_required
def favorite_toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Sprawdzamy, czy produkt jest w ulubionych
    favorite = Favorite.objects.filter(user=request.user, product=product).first()

    if favorite:
        favorite.delete()  # Usuwamy produkt z ulubionych
        is_favorite = False
    else:
        Favorite.objects.create(user=request.user, product=product)  # Dodajemy produkt do ulubionych
        is_favorite = True

    # Zwracamy odpowiedź JSON
    return JsonResponse({'success': True, 'is_favorite': is_favorite})


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
