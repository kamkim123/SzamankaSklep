# orders/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .cart import Cart
from products.models import Product
from .models import Order, OrderItem

import base64
from django.http import HttpResponse, HttpResponseBadRequest
from .epaka import create_epaka_order, epaka_get_document
from django.http import JsonResponse
from .epaka import epaka_api_get


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


@require_http_methods(["GET", "POST"])
def checkout(request):
    cart = Cart(request)
    if request.method == "POST":
        shipping_method = request.POST.get('shipping_method', Order.SHIPPING_INPOST_COURIER)

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
            shipping_cost=cart.shipping,
            status=Order.STATUS_NEW,
            payment_method=request.POST.get('payment_method', Order.PAYMENT_TRANSFER),
            shipping_method=shipping_method,  # 👈 NOWE
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                unit_price=item["price"],
                quantity=item["quantity"],
            )

        # 🔽 TU: próba utworzenia przesyłki w Epace
        access_token = request.session.get("epaka_access_token")
        print("[EPAKA] access_token in session:", bool(access_token))  # DEBUG

        if access_token:
            epaka_data = create_epaka_order(order, access_token)
            if epaka_data is None:
                print(f"[EPAKA] Nie udało się utworzyć przesyłki dla zamówienia {order.pk}")
        else:
            print(f"[EPAKA] Brak access_token w sesji – zamówienie {order.pk} nie wysłane do Epaki")

        cart.clear()
        return redirect("orders:thank_you", pk=order.pk)

    return render(request, "orders/checkout.html", {"cart": cart})


def thank_you(request, pk):
    order = get_object_or_404(Order, pk=pk)
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

    access_token = request.session.get("epaka_access_token")
    if not access_token:
        # jeśli admin/ty nie masz aktualnie tokena w sesji – przekieruj do logowania z Epaką
        return redirect("epaka_login")

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
        return render(request, "epaka_couriers.html", {"couriers": []})

    resp = epaka_api_get("/v1/couriers", access_token)
    data = resp.json()
    couriers = data.get("couriers", [])

    return render(request, "epaka_couriers.html", {"couriers": couriers})

