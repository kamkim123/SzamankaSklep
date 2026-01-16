# orders/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.contrib import messages
import re
from django.views.decorators.cache import never_cache
from .epaka import epaka_check_data, _order_to_epaka_body

from .epaka_auth import get_epaka_access_token

from .cart import Cart
from products.models import Product
from .models import Order, OrderItem

import base64
from django.http import HttpResponse, HttpResponseBadRequest
from .epaka import create_epaka_order, epaka_get_document
from django.http import JsonResponse
from .epaka import epaka_api_get
from django.conf import settings

SHIPPING_PRICES = {
    Order.SHIPPING_INPOST_COURIER: Decimal("18.00"),
    Order.SHIPPING_DPD_COURIER: Decimal("18.00"),
    Order.SHIPPING_INPOST_LOCKER: Decimal("19.00"),
    Order.SHIPPING_PICKUP: Decimal("0.00"),

}

def shipping_for_method(method: str) -> Decimal:
    return SHIPPING_PRICES.get(method, Decimal("0.00"))


@ensure_csrf_cookie
def cart_view(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request):
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity", 1)
    override = request.POST.get("override", "false") == "true"

    product = get_object_or_404(Product, id=product_id)

    cart = Cart(request)
    cart.add(product, quantity=quantity, override_quantity=override)

    return JsonResponse({
        "ok": True,
        "items": len(cart),
        "subtotal": str(cart.subtotal),
        "shipping": str(cart.shipping),
        "grand": str(cart.grand_total),
    })

@require_POST
def cart_remove(request):
    product_id = request.POST.get("product_id")
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    return JsonResponse({
        "ok": True,
        "items": len(cart),  # Liczba produktów w koszyku
        "subtotal": str(cart.subtotal),  # Całkowita wartość produktów
        "shipping": str(cart.shipping),  # Koszt dostawy
        "grand": str(cart.grand_total),  # Łączna kwota
    })


@require_POST
def cart_update_qty(request):
    product_id = request.POST.get("product_id")
    qty = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.add(product, quantity=qty, override_quantity=True)
    item_total = next((i["total_price"] for i in cart if i["product"].id == product.id), Decimal("0"))
    return JsonResponse({
        "ok": True,
        "item_total": str(item_total),
        "items": len(cart),
        "subtotal": str(cart.subtotal),
        "shipping": str(cart.shipping),
        "grand": str(cart.grand_total),
    })


# orders/views.py
@never_cache
@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart(request)

    if request.method == "POST":
        if len(cart) == 0:
            messages.error(request, "Koszyk jest pusty — dodaj produkty i spróbuj ponownie.")
            return redirect("orders:cart")
        shipping_method = request.POST.get("shipping_method", Order.SHIPPING_INPOST_COURIER)
        inpost_locker_code = request.POST.get("inpost_locker_code", "").strip()

        provider = request.POST.get("payment_provider", "transfer")
        if provider == "transfer":
            payment_method = Order.PAYMENT_TRANSFER
        elif provider in ("p24", "card"):
            payment_method = Order.PAYMENT_ONLINE
        else:
            payment_method = Order.PAYMENT_TRANSFER

        shipping_method = (request.POST.get("shipping_method") or Order.SHIPPING_INPOST_COURIER).strip()
        print("POST shipping_method:", repr(shipping_method))
        shipping_cost = shipping_for_method(shipping_method)
        print("CALC shipping_cost:", shipping_cost)

        # --- WALIDACJA TELEFONU ---
        raw_phone = (request.POST.get("phone", "") or "").strip()
        digits = re.sub(r"\D+", "", raw_phone)  # zostaw tylko cyfry

        if len(digits) < 9:
            messages.error(request, "Numer telefonu jest za krótki (min. 9 cyfr).")
            return redirect("orders:checkout")

        if len(digits) > 15:
            messages.error(request, "Numer telefonu jest za długi (max. 15 cyfr).")
            return redirect("orders:checkout")

        postal_code_raw = (request.POST.get("postal_code", "") or "").strip()
        postal_code_raw = postal_code_raw.replace(" ", "").replace("\u00A0", "")  # usuń spacje/NBSP

        # pozwól też na 5 cyfr bez myślnika
        if re.fullmatch(r"\d{5}", postal_code_raw):
            postal_code = postal_code_raw[:2] + "-" + postal_code_raw[2:]
        else:
            postal_code = postal_code_raw

        if not re.fullmatch(r"\d{2}-\d{3}", postal_code):
            messages.error(request, "Nieprawidłowy kod pocztowy. Poprawny format to 00-000.")
            return redirect("orders:checkout")

        city = (request.POST.get("city", "") or "").strip()
        if not city:
            messages.error(request, "Podaj miasto.")
            return redirect("orders:checkout")

        # --- WALIDACJA ePaka: kod pocztowy musi pasować do miasta ---
        access_token = get_epaka_access_token()
        if access_token:
            # Tworzymy "tymczasowy" obiekt order (nie zapisujemy do DB)
            tmp_order = Order(
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                email=request.POST.get('email', ''),
                phone=digits,
                address=request.POST.get('address', ''),
                postal_code=postal_code,
                city=city,
                shipping_method=shipping_method,
                inpost_locker_code=inpost_locker_code,
                shipping_cost=shipping_cost,
                status=Order.STATUS_NEW,
                payment_method=payment_method,
                paid=False,
            )

            # profil ePaki potrzebny do body
            profile_resp = epaka_api_get("/v1/user", access_token)
            if profile_resp.status_code == 200:
                body = _order_to_epaka_body(tmp_order, profile_resp.json())
                check_resp = epaka_check_data(access_token, body)

                if check_resp.status_code != 200:
                    # wyciągnij komunikat
                    try:
                        data = check_resp.json()
                        err = data.get("errors", [{}])[0]
                        msg = err.get("message") or "Nieprawidłowe dane adresowe."
                    except Exception:
                        msg = "Nieprawidłowe dane adresowe."

                    messages.error(request, f"Błąd adresu: {msg}")
                    return redirect("orders:checkout")

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=digits,
            address=request.POST.get('address'),
            postal_code=postal_code,
            city=city,

            shipping_cost=shipping_cost,
            status=Order.STATUS_NEW,
            payment_method=payment_method,

            shipping_method=shipping_method,
            inpost_locker_code=inpost_locker_code,
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                unit_price=item["price"],
                quantity=item["quantity"],
            )



        # ✅ Online: NIE czyścimy koszyka tutaj
        if payment_method == Order.PAYMENT_ONLINE:
            return redirect("orders:p24_start", pk=order.pk)

        # ✅ Offline (transfer): możesz wyczyścić od razu
        cart.clear()
        return redirect("orders:thank_you", pk=order.pk)

    # ======= TO JEST CZĘŚĆ GET (czyli wejście na checkout) =======
    default_method = Order.SHIPPING_INPOST_COURIER
    checkout_shipping = shipping_for_method(default_method)
    checkout_grand = cart.subtotal + checkout_shipping

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "checkout_subtotal": cart.subtotal,
        "checkout_shipping": checkout_shipping,
        "checkout_grand": checkout_grand,
        "checkout_method": default_method,
    })


def thank_you(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.paid:
        Cart(request).clear()


    return render(request, "orders/thank_you.html", {"order": order})


def epaka_label_view(request, pk):
    """
    Zwraca etykietę przewozową z Epaki jako PDF dla danego Order (pk).
    """
    order = get_object_or_404(Order, pk=pk)

    if not order.epaka_order_id:
        return HttpResponseBadRequest(
            "To zamówienie nie ma epaka_order_id – nie zostało wysłane do Epaki."
        )

    access_token = get_epaka_access_token()
    if not access_token:
        return HttpResponseBadRequest("Brak tokena ePaka (server-to-server).")

    # pobieramy dokument typu 'label' (klasyczny PDF)
    resp = epaka_get_document(int(order.epaka_order_id), access_token, doc_type="label")

    if resp.status_code != 200:
        return HttpResponseBadRequest(
            f"Błąd pobierania etykiety z Epaka: {resp.status_code} {resp.text}"
        )

    data = resp.json()
    # wg schematu Document: { "document": "base64-pdf" }
    label_b64 = data.get("document")
    if not label_b64:
        return HttpResponseBadRequest("Brak pola 'document' w odpowiedzi Epaki.")

    try:
        pdf_bytes = base64.b64decode(label_b64)
    except Exception:
        return HttpResponseBadRequest("Nie udało się zdekodować PDF (base64).")

    filename = f"epaka-label-{order.epaka_order_id}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response

def epaka_couriers_view(request):
    access_token = request.session.get("epaka_access_token")
    if not access_token:
        return render(request, "orders/epaka_couriers.html", {"couriers": []})

    resp = epaka_api_get("/v1/couriers", access_token)
    data = resp.json()
    couriers = data.get("couriers", [])

    return render(request, "orders/epaka_couriers.html", {"couriers": couriers})




# orders/views.py

# !!!!!!!!!
#      JAK EPAKA NIE BEDZIE DZIALAC blad 403. to trzeba powiazac konto .../epaka/login powiaz konto. !!!!!!!!
# !!!!!!!!!
def epaka_points(request):
    """
    AJAX: szukanie paczkomatów InPost (courierId = EPAKA_LOCKER_INPOST)
    GET /epaka/points/?q=Nasielsk
    """
    q = (request.GET.get("q") or "").strip()
    if request.method != "GET":
        return JsonResponse({"error": "Only GET allowed"}, status=405)

    if not q:
        return JsonResponse({"points": []})

    access_token = request.session.get("epaka_access_token")
    if not access_token:
        return JsonResponse({"error": "Brak powiązanego konta Epaka"}, status=403)

    params = {
        "limit": 30,
        "query": q,                     # miasto / kod paczkomatu / fragment
        "pointFunction": "receiver",    # odbiór
        "pointType": "machine",         # paczkomaty
        "couriers": [settings.EPAKA_LOCKER_INPOST],  # InPost Paczkomaty
    }

    resp = epaka_api_get("/v1/points", access_token, params=params)
    if resp.status_code != 200:
        # czytelny komunikat dla usera:
        user_msg = "Nie znaleziono paczkomatów. Podaj pełną nazwę miasta lub kod paczkomatu/kod pocztowy."

        return JsonResponse(
            {"error": user_msg, "details": resp.text},
            status=200,  # <-- ważne: frontend nie wejdzie w .fail, tylko w .done
        )

    data = resp.json()  # PointsResponse
    raw_points = data.get("points", [])

    # uproszczona lista dla frontu
    points = []
    for p in raw_points:
        points.append({
            "id": p.get("id"),  # to jest kod typu LAJ01M
            "name": p.get("name"),
            "city": p.get("city"),
            "street": p.get("street"),
            "number": p.get("number"),
            "postCode": p.get("postCode"),
        })

    return JsonResponse({"points": points})



# orders/views.py
from django.contrib.auth.decorators import login_required


@login_required
def order_detail(request, pk):
    # Użytkownik może zobaczyć tylko swoje zamówienie
    order = get_object_or_404(Order, pk=pk, user=request.user)

    # items mamy dzięki related_name="items"
    items = order.items.select_related("product")

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
    })


import json
from uuid import uuid4
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse

from . import p24

def _amount_grosze(order: Order) -> int:
    # total_to_pay masz jako Decimal
    return int((order.total_to_pay * Decimal("100")).quantize(Decimal("1")))

def p24_start(request, pk: int):
    order = get_object_or_404(Order, pk=pk)

    if order.items.count() == 0:
        return HttpResponseBadRequest("Order has no items")

    amount = _amount_grosze(order)
    if amount <= 0:
        return HttpResponseBadRequest("Invalid amount")

    if order.paid:
        return redirect("orders:thank_you", pk=order.pk)

    if not order.p24_session_id:
        order.p24_session_id = f"order-{order.pk}-{uuid4().hex}"
        order.save(update_fields=["p24_session_id"])

    amount = _amount_grosze(order)
    currency = "PLN"

    url_return = request.build_absolute_uri(reverse("orders:thank_you", args=[order.pk]))
    url_status = request.build_absolute_uri(reverse("orders:p24_status"))

    try:
        token, _raw = p24.register_transaction(
            session_id=order.p24_session_id,
            amount=amount,
            currency=currency,
            description=f"Zamówienie #{order.pk}",
            email=order.email,
            url_return=url_return,
            url_status=url_status,
        )
    except Exception as e:
        order.notes = (order.notes or "") + f"\n[P24] register error: {repr(e)}\n"
        # opcjonalnie ustaw status błędu jeśli masz taki:
        # order.status = Order.STATUS_FAILED
        order.save(update_fields=["notes"])  # albo ["notes","status"] jeśli ustawisz status
        messages.error(request, "Nie udało się rozpocząć płatności. Sprawdź e-mail i spróbuj ponownie.")
        return redirect("orders:checkout")

    order.p24_token = token
    order.save(update_fields=["p24_token"])

    # przekierowanie do P24 po TOKEN
    base_url = "https://sandbox.przelewy24.pl" if settings.P24_SANDBOX else "https://secure.przelewy24.pl"
    return redirect(f"{base_url}/trnRequest/{token}")


@csrf_exempt
@require_POST
def p24_status(request):
    """
    WEBHOOK Przelewy24:
    P24 wysyła POST na urlStatus po udanej płatności.
    Tu robimy weryfikację (verify) i dopiero wtedy oznaczamy zamówienie jako opłacone.
    """
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("invalid json")

    session_id = payload.get("sessionId")
    order_id = payload.get("orderId")
    amount = payload.get("amount")
    currency = payload.get("currency", "PLN")
    incoming_sign = payload.get("sign")

    if not (session_id and order_id and amount and incoming_sign):
        return HttpResponseBadRequest("missing fields")

    # --- (OPCJONALNE, ale ok) sprawdzenie sign notyfikacji zgodnie z dokumentacją ---
    origin_amount = int(payload.get("originAmount", amount))
    method_id = int(payload.get("methodId", 0))
    statement = payload.get("statement", "")

    expected = p24.sign_notification(
        merchant_id=settings.P24_MERCHANT_ID,
        pos_id=settings.P24_POS_ID,
        session_id=session_id,
        amount=int(amount),
        origin_amount=origin_amount,
        currency=currency,
        order_id=int(order_id),
        method_id=method_id,
        statement=statement,
        crc=settings.P24_CRC,
    )
    if expected != incoming_sign:
        return HttpResponseBadRequest("bad sign")

    # znajdź zamówienie po sessionId
    order = get_object_or_404(Order, p24_session_id=session_id)

    # idempotencja: P24 może ponowić webhook
    if order.paid:
        return HttpResponse("OK")

    # --- KLUCZOWE: verify ---
    try:
        _verify_resp = p24.verify_transaction(
            session_id=session_id,
            order_id=int(order_id),
            amount=int(amount),
            currency=currency,
        )
    except Exception:
        # zwróć błąd → P24 spróbuje ponownie
        return HttpResponseBadRequest("verify failed")

    # oznacz opłacone
    order.paid = True
    order.paid_at = timezone.now()
    order.status = Order.STATUS_PAID
    order.p24_order_id = str(order_id)
    order.save(update_fields=["paid", "paid_at", "status", "p24_order_id"])

    # ✅ Od teraz NIE wysyłamy automatycznie do ePaki po płatności.
    # Przesyłkę tworzysz ręcznie w adminie akcją "Wyślij do ePaki" po ustawieniu package_size.
    order.epaka_last_error = "Czeka na wybór rozmiaru paczki i ręczne wysłanie do ePaki (admin)."
    order.save(update_fields=["epaka_last_error", "updated_at"])

    return HttpResponse("OK")


