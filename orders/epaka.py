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
        "Content-Type": "application/json",   # 👈 to dodajemy
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
    Buduje body dla /v1/order na podstawie Order + profilu z Epaki
    zgodnie ze schematem z dokumentacji Epaki.
    """
    sender_profile = profile_data["senderData"]

    sender = {
        "name": sender_profile.get("name") or "",
        "lastName": sender_profile.get("lastName") or "",
        "company": sender_profile.get("company") or "",
        "nip": profile_data.get("nip") or "",
        "country": sender_profile.get("country", "PL"),
        "city": sender_profile.get("city") or "",
        "street": sender_profile.get("street") or "",
        "houseNumber": sender_profile.get("houseNumber") or "",
        "flatNumber": sender_profile.get("flatNumber") or "",
        "postCode": sender_profile.get("postCode") or "",
        "phone": sender_profile.get("phone") or "",
        "email": profile_data.get("email") or "",
        "pointId": "",
        "pointDescription": "",
    }

    receiver = {
        "name": order.first_name,
        "lastName": order.last_name,
        "company": "",
        "nip": "",
        "country": "PL",
        "city": order.city,
        "street": order.address,
        "houseNumber": "1",      # uproszczenie na start
        "flatNumber": "",
        "postCode": order.postal_code,
        "phone": order.phone,
        "email": order.email,
        "pointId": "",
        "pointDescription": "",
    }

    payment_data = {
        "paymentType": "balance",   # na start saldo w Epaka, bez operatora p24
        "blikCode": "",
        "paymentOperator": "",
    }

    packages = [
        {
            "weight": 1.0,
            "height": 10,
            "width": 10,
            "length": 10,
            "type": 0,   # ważne: pole nazywa się "type"
        }
    ]

    body = {
        "sender": sender,
        "receiver": receiver,
        "paymentData": payment_data,
        "courierId": 6,               # na sztywno, do dopracowania później
        "shippingType": "package",    # envelope / package / pallet / tires
        "pickupDate": date.today().isoformat(),
        "pickupTime": {"from": "10:30", "to": "14:30"},
        "comments": "",
        "customsService": {
            "purpose": "gift",
            "informationAccept": False,
            "eori": "",
            "pesel": "",
            "hmrc": "",
        },
        "services": {
            "cod": False,
            "codReturnType": "account",
            "codReturnPointId": "",
            "codType": "",
            "codAmount": 0,
            "bankAccount": "",
            "insurance": False,
            "declaredValue": 0,
            "additionalServices": [],
        },
        "packages": packages,
        "content": f"Zamówienie #{order.pk} ze sklepu szamankasklep.pl",
        "contents": [],
        "promoCode": "",
        "tires": {
            "quantity": 0,
            "width": 0,
            "profile": 0,
            "diameter": 0,
        },
    }

    return body


def create_epaka_order(order: Order, access_token: str) -> dict | None:
    """
    Tworzy zamówienie w Epace dla danego Order:
    - pobiera profil /v1/user,
    - buduje payload,
    - robi POST /v1/order,
    - zapisuje epaka_order_id i debug do order.notes.
    """

    def add_note(msg: str):
        order.notes = (order.notes or "") + f"\n[EPAKA] {msg}"
        order.save(update_fields=["notes"])

    # 1. profil
    profile_resp = epaka_api_get("/v1/user", access_token)
    add_note(f"profile status={profile_resp.status_code}")

    if profile_resp.status_code != 200:
        add_note(f"profile error body={profile_resp.text[:500]}")
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
        return None

    data = resp.json()
    add_note(f"order json keys={list(data.keys())}")

    # tu REALNIE ustawiamy epaka_order_id w modelu:
    order.epaka_order_id = str(
        data.get("orderId")
        or data.get("id")
        or data.get("order_id")
        or ""
    )
    order.save(update_fields=["epaka_order_id", "notes"])

    return data
