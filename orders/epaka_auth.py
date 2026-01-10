import requests
from django.conf import settings
from django.utils import timezone

from .models import EpakaToken

def get_epaka_access_token() -> str | None:
    # 1) spróbuj z DB (cache)
    cached = EpakaToken.get_valid()
    if cached:
        return cached

    # 2) pobierz nowy token (client_credentials)
    try:
        resp = requests.post(
            settings.EPAKA_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": settings.EPAKA_CLIENT_ID,
                "client_secret": settings.EPAKA_CLIENT_SECRET,
            },
            timeout=20,
        )
    except Exception:
        return None

    if resp.status_code != 200:
        return None

    data = resp.json()
    token = data.get("access_token")
    expires_in = int(data.get("expires_in") or 3600)
    if not token:
        return None

    expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)

    # zapisz/odśwież
    EpakaToken.objects.all().delete()  # trzymamy 1 rekord
    EpakaToken.objects.create(access_token=token, expires_at=expires_at)
    return token
