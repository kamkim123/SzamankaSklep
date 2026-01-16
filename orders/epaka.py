# orders/epaka.py
import requests
from datetime import date, timedelta
from django.conf import settings
import re
from .models import Order


# Mapowanie rozmiaru paczki -> wymiary dla ePaki (dostosuj do siebie)
PACKAGE_DIMENSIONS = {
    "S": {"weight": 1.0, "height": 10, "width": 20, "length": 30},
    "M": {"weight": 3.0, "height": 20, "width": 30, "length": 40},
    "L": {"weight": 6.0, "height": 35, "width": 30, "length": 50},
}


def epaka_api_get(endpoint, access_token, params=None):
    url = settings.EPAKA_API_BASE_URL.rstrip("/") + endpoint
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        # UWAGA: NIE dajemy Content-Type do GET
    }
    return requests.get(url, headers=headers, params=params or {}, timeout=20)





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
    Zwraca najbliższy dzień roboczy (pn–pt) >= start.
    """
    d = start
    while d.weekday() >= 5:  # 5 = sobota, 6 = niedziela
        d += timedelta(days=1)
    return d


# orders/epaka.py



def _order_to_epaka_body(order: Order, profile_data: dict) -> dict:
    sender = profile_data["senderData"]
    default_points = profile_data.get("defaultPoints") or []
    default_point = default_points[0] if default_points else {}

    # --- 1. wybór kuriera i trybu punktów ---
    if order.shipping_method == Order.SHIPPING_INPOST_COURIER:
        # InPost KURIER – door-to-door
        courier_id = getattr(settings, "EPAKA_COURIER_INPOST", 12)
        use_point_for_sender = False
        use_point_for_receiver = False

    elif order.shipping_method == Order.SHIPPING_INPOST_LOCKER:
        # InPost PACZKOMAT – odbiorca = paczkomat
        courier_id = getattr(settings, "EPAKA_LOCKER_INPOST", 6)
        use_point_for_sender = True
        use_point_for_receiver = True

    elif order.shipping_method == Order.SHIPPING_DPD_COURIER:
        courier_id = getattr(settings, "EPAKA_COURIER_DPD", 1)
        use_point_for_sender = False
        use_point_for_receiver = False

    else:
        # fallback – np. pickup, ale jak już leci do Epaki, to niech leci InPost Kurierem
        courier_id = getattr(settings, "EPAKA_COURIER_INPOST", 12)
        use_point_for_sender = False
        use_point_for_receiver = False

    # --- 2. pointId / pointDescription dla nadawcy ---
    sender_point_id = ""
    sender_point_desc = ""
    if use_point_for_sender and default_point:
        sender_point_id = default_point.get("id", "")
        sender_point_desc = default_point.get("name", "")

    # --- 3. pointId / pointDescription dla odbiorcy ---
    receiver_point_id = ""
    receiver_point_desc = ""

    if use_point_for_receiver:
        # 👇 TU JEST CAŁA MAGIA: jeśli klient podał kod paczkomatu – używamy GO
        if order.inpost_locker_code:
            receiver_point_id = order.inpost_locker_code
            receiver_point_desc = order.inpost_locker_code
        elif default_point:
            # fallback: domyślny punkt z profilu, jeśli coś nie pykło
            receiver_point_id = default_point.get("id", "")
            receiver_point_desc = default_point.get("name", "")

    street = (order.address or "").strip()
    house_number = "1"
    flat_number = ""

    # np. "Kwiatowa 12/3" albo "Kwiatowa 12-3" albo "Kwiatowa 12"
    m = re.search(r"(.+?)\s+(\d+[A-Za-z]?)(?:[\ /\- ](\d+[A-Za-z]?))?$", street)
    if m:
        street = m.group(1).strip()
        house_number = m.group(2)
        flat_number = m.group(3) or ""
    # --- 4. odbiorca ---
    receiver = {
        "name": order.first_name,
        "lastName": order.last_name,
        "company": "",
        "nip": "",
        "country": "PL",
        "city": order.city,
        "street": street,
        "houseNumber": house_number,
        "flatNumber": flat_number,
        "postCode": order.postal_code,
        "phone": order.phone,
        "email": order.email,
        "pointId": receiver_point_id,
        "pointDescription": receiver_point_desc,
    }

    # --- 5. nadawca ---
    sender_payload = {
        "name": sender["name"],
        "lastName": sender["lastName"],
        "company": sender.get("company", ""),
        "nip": profile_data.get("nip", ""),
        "country": sender.get("country", "PL"),
        "city": sender["city"],
        "street": sender["street"],
        "houseNumber": sender["houseNumber"],
        "flatNumber": sender.get("flatNumber", ""),
        "postCode": sender["postCode"],
        "phone": sender["phone"],
        "email": profile_data.get("email", ""),
        "pointId": sender_point_id,
        "pointDescription": sender_point_desc,
    }

    # --- 6. płatność, paczki, usługi ---
    payment_data = {
        "paymentType": "balance",
    }

    # --- 6.1. paczka: wymiary zależne od wybranego rozmiaru w adminie ---
    dims = PACKAGE_DIMENSIONS.get(order.package_size)

    # jeśli brak rozmiaru, nie pozwalamy wysłać do ePaki
    if not dims:
        raise ValueError("Brak wybranego rozmiaru paczki (package_size). Ustaw S/M/L w adminie.")

    packages = [
        {
            "weight": float(dims["weight"]),
            "height": int(dims["height"]),
            "width": int(dims["width"]),
            "length": int(dims["length"]),
            "type": 0,
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
        "declaredValue": float(order.total_to_pay),
        "additionalServices": [],
    }

    pickup_date = _nearest_workday(date.today() + timedelta(days=1))

    body = {
        "sender": sender_payload,
        "receiver": receiver,
        "paymentData": payment_data,
        "courierId": courier_id,
        "shippingType": "package",
        "pickupDate": pickup_date.isoformat(),
        "pickupTime": {"from": "09:00", "to": "17:00"},
        "comments": "",
        "services": services,
        "packages": packages,
        "content": f"Zamówienie #{order.pk} ze sklepu szamankasklep.pl",
        "promoCode": "",
    }

    return body



def create_epaka_order(order: Order, access_token: str) -> dict | None:
    if not order.paid or order.status != Order.STATUS_PAID:
        order.epaka_last_error = "Nie wysłano do ePaki: zamówienie nie jest opłacone."
        order.save(update_fields=["epaka_last_error", "updated_at"])
        return None

    if order.epaka_order_id:
        order.epaka_last_error = "Nie wysłano do ePaki: zamówienie już ma epaka_order_id."
        order.save(update_fields=["epaka_last_error", "updated_at"])
        return None

    if not order.package_size:
        order.epaka_last_error = "Nie wysłano do ePaki: brak package_size (S/M/L)."
        order.save(update_fields=["epaka_last_error", "updated_at"])
        return None

    profile_resp = epaka_api_get("/v1/user", access_token)

    if profile_resp.status_code != 200:
        order.epaka_last_error = f"EPAKA /v1/user status={profile_resp.status_code}"
        order.notes = (order.notes or "") + (
            f"\n[EPAKA] /v1/user status={profile_resp.status_code}\n"
            f"[EPAKA] /v1/user body={profile_resp.text[:2000]}\n"
        )
        order.save(update_fields=["epaka_last_error", "notes", "updated_at"])
        return None

    profile_data = profile_resp.json()

    try:
        body = _order_to_epaka_body(order, profile_data)
    except ValueError as e:
        order.epaka_last_error = str(e)
        order.notes = (order.notes or "") + f"\n[EPAKA] ERROR: {e}\n"
        order.save(update_fields=["epaka_last_error", "notes", "updated_at"])
        return None

    order.notes = (order.notes or "") + (
        f"\n[EPAKA-debug] shipping_method={order.shipping_method} "
        f"courierId={body.get('courierId')} "
        f"pickupDate={body.get('pickupDate')}\n"
    )

    order.notes = (order.notes or "") + (
        f"\n[EPAKA-debug-body] receiver.pointId={body.get('receiver', {}).get('pointId')} "
        f"receiver.pointDescription={body.get('receiver', {}).get('pointDescription')}\n"
    )
    order.save(update_fields=["notes"])

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
