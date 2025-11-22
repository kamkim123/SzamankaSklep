# orders/epaka.py
import requests
from datetime import date
from django.conf import settings

from .models import Order


def epaka_api_get(endpoint, access_token, params=None):
    url = settings.EPAKA_API_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    return requests.get(url, headers=headers, params=params or {})


def epaka_api_post(endpoint, access_token, payload):
    url = settings.EPAKA_API_BASE_URL + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    return requests.post(url, headers=headers, json=payload)


def _order_to_epaka_body(order: Order, profile_data: dict) -> dict:
    """
    Buduje body dla /v1/order na podstawie Order + profilu z Epaki.
    Tu jest wersja MINIMALNA – później dopasujemy kuriera, wymiary itd.
    """

    sender = profile_data["senderData"]

    receiver = {
        "name": order.first_name,
        "lastName": order.last_name,
        "company": "",
        "country": "PL",
        # uproszczenie: całość w address, numer domu "1"
        "street": order.address,
        "houseNumber": "1",
        "flatNumber": "",
        "postCode": order.postal_code,
        "city": order.city,
        "phone": order.phone,
        "email": order.email,
    }

    # Płatność po stronie Epaki – na początek saldo w panelu Epaki
    payment_data = {
        "paymentType": "balance",   # możesz zmienić np. na 'online_payment'
    }

    # Na razie załóżmy 1 paczkę o domyślnych wymiarach:
    packages = [
        {
            "weight": 1.0,   # kg – później można policzyć z produktów
            "height": 10,
            "width": 10,
            "length": 10,
        }
    ]

    # Wybór kuriera – docelowo weźmiesz z /v1/couriers albo defaultPoints
    courier_id = 6  # przykładowy ID (np. InPost/GLS) – zmienisz jak poznasz z dokumentacji

    body = {
        "sender": sender,
        "receiver": receiver,
        "paymentData": payment_data,
        "courierId": courier_id,
        "shippingType": "package",  # envelope / package / pallet / tires
        "pickupDate": date.today().isoformat(),
        "pickupTime": {"from": "10:00", "to": "16:00"},
        "content": f"Zamówienie #{order.pk} ze sklepu szamankasklep.pl",
        "packages": packages,
        # na start bez usług dodatkowych:
        # "services": {...},
        # "customsService": {...},
        # "contents": [...]
    }

    return body


def create_epaka_order(order: Order, access_token: str) -> dict | None:
    """
    Tworzy zamówienie w Epace dla danego Order:
    - pobiera profil /v1/user (dla senderData),
    - buduje payload,
    - wywołuje POST /v1/order,
    - zapisuje epaka_order_id, ew. debug w order.notes.
    """

    # mały helper do dopisywania notatek
    def add_note(msg: str):
        order.notes = (order.notes or "") + f"\n[EPAKA] {msg}"
        order.save(update_fields=["notes"])

    # 1. profil (senderData)
    profile_resp = epaka_api_get("/v1/user", access_token)
    add_note(f"profile status={profile_resp.status_code}")

    if profile_resp.status_code != 200:
        add_note(f"profile error body={profile_resp.text[:500]}")
        print("Epaka profile error:", profile_resp.status_code, profile_resp.text)
        return None

    profile_data = profile_resp.json()

    # 2. body
    body = _order_to_epaka_body(order, profile_data)
    add_note(f"request body={body}")

    # 3. POST /v1/order
    resp = epaka_api_post("/v1/order", access_token, body)
    add_note(f"order status={resp.status_code}")
    add_note(f"order raw body={resp.text[:1000]}")

    if resp.status_code != 200:
        print("Epaka order error:", resp.status_code, resp.text)
        return None

    data = resp.json()
    add_note(f"order json keys={list(data.keys())}")

    order.epaka_order_id = str(
        data.get("orderId")
        or data.get("id")
        or data.get("order_id")
        or ""
    )
    order.save(update_fields=["epaka_order_id", "notes"])

    return data


