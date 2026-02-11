# newsletter/views.py
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import NewsletterSubscriber

@require_POST
def signup(request):
    email = (request.POST.get("email") or "").strip().lower()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if not email:
        messages.error(request, "Wpisz adres e-mail.")
        return redirect(next_url)

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "Podaj poprawny adres e-mail.")
        return redirect(next_url)

    obj, created = NewsletterSubscriber.objects.get_or_create(email=email)

    if created:
        messages.success(request, "Dziękujemy! Twój e-mail został zapisany do newslettera.")
    else:

        if obj.is_active:
            messages.info(request, "Ten e-mail jest już zapisany do newslettera.")
        else:
            obj.is_active = True
            obj.save(update_fields=["is_active"])
            messages.success(request, "Super! Ponownie aktywowaliśmy Twój zapis do newslettera.")

    return redirect(next_url)

