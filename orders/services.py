from decimal import Decimal
from django.db import transaction
from .models import Order, OrderItem

@transaction.atomic
def create_order_from_cart(*, cart, data: dict, user=None, shipping_cost: Decimal = Decimal("0.00")) -> Order:
    """
    Tworzy Order + OrderItem na podstawie koszyka.
    cart: obiekt Cart z relacją items -> (product, quantity)
    data: dane formularza: first_name, last_name, email, phone, address, postal_code, city, payment_method (opcjonalnie notes)
    user: zalogowany użytkownik (albo None dla gościa)
    shipping_cost: koszt dostawy (Decimal)
    """
    order = Order.objects.create(
        user=user,
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        phone=data.get("phone", ""),
        address=data["address"],
        postal_code=data["postal_code"],
        city=data["city"],
        payment_method=data.get("payment_method", Order.PAYMENT_TRANSFER),
        shipping_cost=shipping_cost,
        status=Order.STATUS_NEW,
        paid=False,
        notes=data.get("notes", ""),
    )

    # przenieś pozycje koszyka
    # zakładam models.Cart/CartItem w bazie z related_name="items"
    for item in cart.items.select_related("product"):
        product = item.product
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=getattr(product, "name", str(product)),
            unit_price=product.price,   # snapshot ceny
            quantity=item.quantity,
        )

    # wyczyść koszyk (dla koszyka w DB)
    cart.items.all().delete()
    # lub jeśli wolisz skasować cały koszyk:
    # cart.delete()

    return order
