from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.encoding import force_str
from django.views.decorators.http import require_http_methods
from .forms import SignupForm, EmailAuthenticationForm
from .models import Favorite, Profile
from products.models import Product
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.contrib import messages


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .forms import UserUpdateForm, ProfileUpdateForm, AddressForm
from .models import Address, Profile


def home(request):
    return render(request, "home.html")


def _mask_email(email: str) -> str:
    try:
        local, domain = email.split("@")
        dom, *tld = domain.split(".")
        def m(s: str) -> str:
            if len(s) <= 2: return s[0] + "*"
            return s[0] + "*" * (len(s) - 2) + s[-1]
        suffix = ".".join(tld)
        return f"{m(local)}@{m(dom)}{('.' + suffix) if suffix else ''}"
    except Exception:
        return email



from django.conf import settings
import logging
logger = logging.getLogger(__name__)

def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())

    # Dla testów lepiej generować link z aktualnej domeny:
    domain = get_current_site(request).domain  # np. 127.0.0.1:8000 lokalnie
    scheme = "https" if request.is_secure() else "http"
    link = f"{scheme}://{domain}/u/activate/{uid}/{token}/"

    message_html = render_to_string('users/activation_email.html', {
        'user': user,
        'activation_link': link,
    })

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or settings.EMAIL_HOST_USER

    try:
        sent = send_mail(
            subject='Aktywacja konta',
            message=f'Aktywuj konto: {link}',
            from_email=from_email,
            recipient_list=[user.email],
            html_message=message_html,
            fail_silently=False,
        )
        logger.info("Activation email sent=%s to=%s from=%s", sent, user.email, from_email)
    except Exception as e:
        logger.exception("Activation email FAILED for %s: %s", user.email, e)
        raise



def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Aktywuj konto użytkownika
        user.is_active = True
        user.save(update_fields=["is_active"])
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
            user.is_active = False
            user.save(update_fields=["is_active"])

            # (masz już poprawioną funkcję, która wysyła maila z dobrym from_email)
            send_activation_email(user, request)

            # ⬇️ zapisz zamaskowany email i PRG
            request.session["signup_email_hint"] = _mask_email(user.email)
            return redirect("users:signup_email_sent")

        return render(request, "users/register.html", {"form": form})

    return render(request, "users/register.html", {"form": SignupForm()})


def signup_email_sent(request):
    email_hint = request.session.pop("signup_email_hint", None)  # jednorazowo
    return render(request, "users/email_sent.html", {"email_hint": email_hint})

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
    profile = getattr(request.user, "profile", None)
    addresses = profile.addresses.all() if profile else []
    orders = getattr(getattr(request.user, "orders", None), "all", lambda: [])()
    favorites = Favorite.objects.select_related("product").filter(user=request.user)
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


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile


@login_required
def edit_profile(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        uform = UserUpdateForm(request.POST, instance=user)
        pform = ProfileUpdateForm(request.POST, instance=profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()  # Zapisanie danych użytkownika
            pform.save()  # Zapisanie danych profilu

            if request.is_ajax():  # Sprawdzamy, czy to jest żądanie AJAX
                return JsonResponse({
                    "ok": True,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": profile.phone,
                })

            messages.success(request, "Twoje dane zostały zaktualizowane!")
            return redirect("users:user-panel")

        else:
            if request.is_ajax():
                return JsonResponse({"ok": False, "errors": {
                    "user": uform.errors,
                    "profile": pform.errors
                }}, status=400)

    else:
        uform = UserUpdateForm(instance=user)
        pform = ProfileUpdateForm(instance=profile)

    return render(request, "users/edit_profile.html", {"uform": uform, "pform": pform})





@login_required
def add_address(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.profile = profile
            address.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "ok": True,
                    "id": address.id,
                    "address_line_1": address.address_line_1,
                    "city": address.city,
                    "postal_code": address.postal_code,
                })
            messages.success(request, "Dodano adres.")
            return redirect("users:user-panel")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        form = AddressForm()
    return render(request, "users/address_form.html", {"form": form, "mode": "add"})

@login_required
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if address.profile.user_id != request.user.id:
        return HttpResponseForbidden("Brak uprawnień.")

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "ok": True,
                    "id": address.id,
                    "address_line_1": address.address_line_1,
                    "city": address.city,
                    "postal_code": address.postal_code,
                })
            messages.success(request, "Zapisano adres.")
            return redirect("users:user-panel")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
    else:
        form = AddressForm(instance=address)
    return render(request, "users/address_form.html", {"form": form, "mode": "edit", "address": address})

@login_required
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    if address.profile.user_id != request.user.id:
        return HttpResponseForbidden("Brak uprawnień.")
    if request.method == "POST":
        address.delete()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": True})
        messages.success(request, "Usunięto adres.")
        return redirect("users:user-panel")
    return HttpResponseBadRequest("Nieprawidłowe żądanie.")


import logging
