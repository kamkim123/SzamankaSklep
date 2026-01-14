import hashlib
import json
from collections import OrderedDict
import requests
from django.conf import settings

def _sha384_of_json(ordered_dict: OrderedDict) -> str:
    # P24 wymaga SHA-384 z JSON bez escapowania slashy/unicode i bez zbędnych spacji
    s = json.dumps(ordered_dict, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha384(s.encode("utf-8")).hexdigest()

def sign_register(session_id: str, merchant_id: int, amount: int, currency: str, crc: str) -> str:
    params = OrderedDict([
        ("sessionId", session_id),
        ("merchantId", merchant_id),
        ("amount", amount),
        ("currency", currency),
        ("crc", crc),
    ])
    return _sha384_of_json(params)

def sign_verify(session_id: str, order_id: int, amount: int, currency: str, crc: str) -> str:
    params = OrderedDict([
        ("sessionId", session_id),
        ("orderId", order_id),
        ("amount", amount),
        ("currency", currency),
        ("crc", crc),
    ])
    return _sha384_of_json(params)

def register_transaction(*, session_id: str, amount: int, currency: str, description: str, email: str, url_return: str, url_status: str):
    payload = {
        "merchantId": settings.P24_MERCHANT_ID,
        "posId": settings.P24_POS_ID,
        "sessionId": session_id,
        "amount": amount,          # w groszach (int)
        "currency": currency,
        "description": description,
        "email": email,
        "country": "PL",
        "language": "pl",
        "urlReturn": url_return,
        "urlStatus": url_status,
        "sign": sign_register(session_id, settings.P24_MERCHANT_ID, amount, currency, settings.P24_CRC),
    }

    r = requests.post(
        f"{settings.P24_API_BASE}/transaction/register",
        json=payload,
        auth=(str(settings.P24_POS_ID), settings.P24_API_KEY),
        timeout=20,
    )

    if r.status_code >= 400:
        raise RuntimeError(f"P24 register failed status={r.status_code} body={r.text}")

    data = r.json()

    # najczęściej: data["data"]["token"]
    token = (data.get("data") or {}).get("token") or data.get("token")
    if not token:
        raise RuntimeError(f"Brak tokena w odpowiedzi P24: {data}")
    return token, data

def verify_transaction(*, session_id: str, order_id: int, amount: int, currency: str):
    payload = {
        "merchantId": settings.P24_MERCHANT_ID,
        "posId": settings.P24_POS_ID,
        "sessionId": session_id,
        "amount": amount,
        "currency": currency,
        "orderId": order_id,
        "sign": sign_verify(session_id, order_id, amount, currency, settings.P24_CRC),
    }

    r = requests.put(
        f"{settings.P24_API_BASE}/transaction/verify",
        json=payload,
        auth=(str(settings.P24_POS_ID), settings.P24_API_KEY),
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

# w orders/p24.py
def sign_notification(*, merchant_id: int, pos_id: int, session_id: str, amount: int, origin_amount: int,
                      currency: str, order_id: int, method_id: int, statement: str, crc: str) -> str:
    params = OrderedDict([
        ("merchantId", merchant_id),
        ("posId", pos_id),
        ("sessionId", session_id),
        ("amount", amount),
        ("originAmount", origin_amount),
        ("currency", currency),
        ("orderId", order_id),
        ("methodId", method_id),
        ("statement", statement),
        ("crc", crc),
    ])
    return _sha384_of_json(params)


def test_access():
    r = requests.get(
        f"{settings.P24_API_BASE}/testAccess",
        auth=(str(settings.P24_POS_ID), settings.P24_API_KEY),
        timeout=20,
    )
    r.raise_for_status()
    return r.json()