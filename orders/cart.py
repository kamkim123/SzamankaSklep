from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID, {})

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def add(self, product: Product, quantity=1, override_quantity=False):
        pid = str(product.id)
        item = self.cart.get(pid, {"quantity": 0, "price": None})

        # KLUCZOWE: cena jako STRING w sesji (nie Decimal!)
        if item["price"] is None:
            item["price"] = str(product.price)  # np. "129.99"

        quantity = int(quantity)
        if override_quantity:
            item["quantity"] = quantity
        else:
            item["quantity"] += quantity

        if item["quantity"] <= 0:
            self.cart.pop(pid, None)
        else:
            self.cart[pid] = item

        self.save()

    def remove(self, product: Product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for p in products:
            raw = self.cart[str(p.id)]
            price = Decimal(raw["price"])  # do rachunków
            qty = int(raw["quantity"])
            yield {
                "product": p,
                "price": price,  # Decimal tylko w Pythonie
                "quantity": qty,
                "total_price": price * qty,  # Decimal
            }

    def __len__(self):
        return sum(int(i["quantity"]) for i in self.cart.values())

    @property
    def subtotal(self) -> Decimal:
        return sum(Decimal(i["price"]) * int(i["quantity"]) for i in self.cart.values()) or Decimal("0")

    @property
    def shipping(self) -> Decimal:
        return Decimal("0") if self.subtotal >= Decimal("200") else Decimal("15")

    @property
    def grand_total(self) -> Decimal:
        return self.subtotal + self.shipping

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.session.modified = True
