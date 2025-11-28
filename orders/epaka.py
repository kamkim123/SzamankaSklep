# orders/epaka.py
import requests
from datetime import date, timedelta
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



def _nearest_workday(start: date) -> date:
    """
    Zwraca najbliższy dzień roboczy >= start (pn–pt).
    """
    d = start
    while d.weekday() >= 5:  # 5 = sobota, 6 = niedziela
        d += timedelta(days=1)
    return d


def _order_to_epaka_body(order: Order, profile_data: dict) -> dict:
    sender = profile_data["senderData"]

    default_points = profile_data.get("defaultPoints") or []
    default_point = default_points[0] if default_points else {}

    if order.shipping_method == Order.SHIPPING_INPOST_COURIER:
        courier_id = getattr(settings, "EPAKA_COURIER_INPOST", 12)
    elif order.shipping_method == Order.SHIPPING_DPD_COURIER:
        courier_id = getattr(settings, "EPAKA_COURIER_DPD", 1)
    elif order.shipping_method == Order.SHIPPING_INPOST_LOCKER:
        courier_id = getattr(settings, "EPAKA_LOCKER_INPOST", 6)
    else:  # SHIPPING_PICKUP – możesz tu np. dać DHL
        courier_id = getattr(settings, "EPAKA_COURIER_DHL", 8)


    receiver = {
        "name": order.first_name,
        "lastName": order.last_name,
        "company": "",
        "nip": "",
        "country": "PL",
        "city": order.city,
        "street": order.address,
        "houseNumber": "1",
        "flatNumber": "",
        "postCode": order.postal_code,
        "phone": order.phone,
        "email": order.email,
    }

    if order.shipping_method == Order.SHIPPING_INPOST_LOCKER:
        receiver["pointId"] = default_point.get("id", "")
        receiver["pointDescription"] = default_point.get("name", "")

    sender_payload = {
        "name": sender["name"],
        "lastName": sender["lastName"],
        "company": sender["company"],
        "nip": profile_data.get("nip", ""),
        "country": sender["country"],
        "city": sender["city"],
        "street": sender["street"],
        "houseNumber": sender["houseNumber"],
        "flatNumber": sender.get("flatNumber", ""),
        "postCode": sender["postCode"],
        "phone": sender["phone"],
        "email": profile_data.get("email", sender["phone"]),
        "pointId": default_point.get("id", ""),
        "pointDescription": default_point.get("name", ""),
    }

    payment_data = {
        "paymentType": "balance",   # jak w panelu, z salda
    }

    # na sztywno podobnie jak na screenie
    packages = [
        {
            "weight": 6.0,
            "height": 35,
            "width": 30,
            "length": 25,
            "type": 0,   # tu później dopasujemy do „sortowalne”, jeśli podadzą enum
        }
    ]

    services = {
        "cod": False,
        "codReturnType": "account",
        "codReturnPointId": "",
        "codType": "",
        "codAmount": 0,
        "bankAccount": "",
        "insurance": True,
        "declaredValue": float(order.total_to_pay),  # np. wartość zamówienia
        "additionalServices": [],  # tu kiedyś dorzucimy SMS wg kodu z /v1/order/services
    }

    pickup_date = _nearest_workday(date.today() + timedelta(days=1)).isoformat()

    body = {
        "sender": sender_payload,
        "receiver": receiver,
        "paymentData": payment_data,
        "courierId": courier_id,
        "shippingType": "package",
        "pickupDate": pickup_date,
        "pickupTime": {"from": "10:30", "to": "14:30"},
        "comments": "",
        "customsService": {
            "purpose": "gift",
            "informationAccept": False,
            "eori": "",
            "pesel": "",
            "hmrc": "",
        },
        "services": services,
        "packages": packages,
        "content": f"Zamówienie #{order.pk} ze sklepu szamankasklep.pl",
        "contents": [],
        "promoCode": "",
        "tires": {"quantity": 0, "width": 0, "profile": 0, "diameter": 0},

    }

    return body




def create_epaka_order(order: Order, access_token: str) -> dict | None:
    profile_resp = epaka_api_get("/v1/user", access_token)
    if profile_resp.status_code != 200:
        order.notes = (order.notes or "") + (
            f"\n[EPAKA] profile status={profile_resp.status_code}\n"
            f"[EPAKA] profile body={profile_resp.text}\n"


        )
        order.save(update_fields=["notes"])
        return None

    profile_data = profile_resp.json()

    body = _order_to_epaka_body(order, profile_data)

    order.notes = (order.notes or "") + (
        f"\n[EPAKA-debug] shipping_method={order.shipping_method} "
        f"courierId={body.get('courierId')} "
        f"pickupDate={body.get('pickupDate')}\n"
    )

    # 2.5. check-data – sprawdzenie po stronie Epaki
    check_resp = epaka_check_data(access_token, body)
    order.notes = (order.notes or "") + f"\n[EPAKA-check] {check_resp.status_code} {check_resp.text[:1000]}"
    order.save(update_fields=["notes"])

    # 👇 debug: zapisz, jaki kurier idzie do Epaki
    order.notes = (order.notes or "") + (
        f"\n[EPAKA-debug] shipping_method={order.shipping_method} courierId={body.get('courierId')}\n"
    )
    order.save(update_fields=["notes"])

    if check_resp.status_code != 200:
        print("[EPAKA] check-data ERROR", check_resp.status_code, check_resp.text)
        return None

    # 3. POST /v1/order
    resp = epaka_api_post("/v1/order", access_token, body)

    # <--- logujemy ZAWSZE
    try:
        raw = resp.text
    except Exception:
        raw = "<no text>"

    order.notes = (order.notes or "") + (
        f"\n[EPAKA] order status={resp.status_code}\n"
        f"[EPAKA] order raw={raw}\n"
    )
    order.save(update_fields=["notes"])

    if resp.status_code not in (200, 201):
        return None

    data = resp.json()

    # zapisujemy ID i wynik procesu
    order.epaka_order_id = str(data.get("orderId") or "")
    msg = data.get("message", "")
    result = data.get("orderProcessResult", "")
    order.notes += f"\n[EPAKA] orderId={order.epaka_order_id} " \
                   f"result={result} message={msg}\n"
    order.save(update_fields=["epaka_order_id", "notes"])

    # tylko jeśli result == 1, mamy „pełne” zamówienie z etykietą
    return data


# orders/epaka.py

def epaka_get_document(order_epaka_id: int, access_token: str, doc_type: str = "label"):
    """
    Pobiera dokument (etykietę, protokół, itd.) z Epaki dla danego zamówienia.
    doc_type:
      - label
      - label-zebra
      - proforma
      - protocol
      - authorization-document
      - exporter-statement
      - lv-document
      - hvEcx-document
    """
    endpoint = f"/v1/user/orders/{order_epaka_id}/{doc_type}"
    return epaka_api_get(endpoint, access_token)


def epaka_check_data(access_token: str, body: dict):
    return epaka_api_post("/v1/order/check-data", access_token, body)


def epaka_get_prices(access_token: str, *, sender_postcode: str, receiver_postcode: str,
                     weight: float, height: int, width: int, length: int):
    payload = {
        "shippingType": "package",
        "senderCountry": "PL",
        "receiverCountry": "PL",
        "senderPostCode": sender_postcode,
        "receiverPostCode": receiver_postcode,
        "packages": [{
            "weight": weight,
            "height": height,
            "width": width,
            "length": length,
            "type": 0,
        }],
    }
    return epaka_api_post("/v1/order/prices", access_token, payload)
