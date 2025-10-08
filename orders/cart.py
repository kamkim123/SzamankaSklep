# orders/cart.py
from decimal import Decimal
from django.conf import settings
from products.models import Product  # zakładam, że tak nazywa się model

CART_SESSION_ID = getattr(settings, "CART_SESSION_ID", "cart")

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product: Product, quantity=1, override_quantity=False):
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[pid]["quantity"] = int(quantity)
        else:
            self.cart[pid]["quantity"] += int(quantity)
        if self.cart[pid]["quantity"] <= 0:
            self.remove(product)
        self.save()

    def remove(self, product: Product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def subtotal(self):
        from decimal import Decimal
        return sum(Decimal(i["price"]) * i["quantity"] for i in self.cart.values())

    @property
    def shipping(self):
        # Dostawa 0 zł od 200 zł – jak w Twoim UI
        return Decimal("0.00") if self.subtotal >= Decimal("200") else Decimal("15.00")

    @property
    def grand_total(self):
        return self.subtotal + self.shipping
