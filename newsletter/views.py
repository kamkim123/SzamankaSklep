from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber

@require_POST
def signup(request):
    email = (request.POST.get("email") or "").strip().lower()
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if email:
        NewsletterSubscriber.objects.get_or_create(email=email)

    return redirect(next_url)
