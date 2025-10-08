# orders/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

from .cart import Cart
from products.models import Product
from .models import Order, OrderItem


@ensure_csrf_cookie
def cart_view(request):
    cart = Cart(request)
    return render(request, "orders/cart.html", {"cart": cart})


@require_POST
def cart_add(request):
    product_id = request.POST.get("product_id")
    quantity = request.POST.get("quantity", 1)
    override = request.POST.get("override", "false") == "true"

    # Debugowanie: sprawdzenie otrzymanych danych
    print("Otrzymane dane:", product_id, quantity, override)

    # Sprawdzenie, czy produkt istnieje
    try:
        product = get_object_or_404(Product, id=product_id)
    except Exception as e:
        print(f"Błąd podczas szukania produktu: {e}")
        return JsonResponse({"ok": False, "error": "Produkt nie znaleziony"}, status=404)

    # Debugowanie: Sprawdzenie produktu
    print("Produkt znaleziony:", product.product_name, product.id)

    cart = Cart(request)
    cart.add(product, quantity=quantity, override_quantity=override)

    # Debugowanie: stan koszyka po dodaniu produktu
    print("Stan koszyka po dodaniu:", cart.__dict__)  # Może zawierać informacje o liczbie produktów, subtotalu itp.

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
        # Stworzenie zamówienia
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address'),
            postal_code=request.POST.get('postal_code'),
            city=request.POST.get('city'),
            shipping_cost=cart.shipping,  # Koszt wysyłki
            status=Order.STATUS_NEW,  # Początkowy status
            payment_method=request.POST.get('payment_method', Order.PAYMENT_TRANSFER),
            # Można dodać płatność przez POST
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                unit_price=item["price"],  # Zapisujemy cenę z koszyka
                quantity=item["quantity"],
            )

        cart.clear()  # Czyszczenie koszyka po utworzeniu zamówienia
        return redirect("orders:thank_you", pk=order.pk)

    return render(request, "orders/checkout.html", {"cart": cart})


def thank_you(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, "orders/thank_you.html", {"order": order})

