from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from products.models import Product

MONEY_Q = Decimal("0.01")

def qmoney(x: Decimal) -> Decimal:
    return x.quantize(MONEY_Q, rounding=ROUND_HALF_UP)

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

        # Zawsze zapisuj aktualną cenę (promo albo normalna)
        item["price"] = str(product.effective_price)

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
            price = Decimal(raw["price"])
            qty = int(raw["quantity"])
            yield {
                "product": p,
                "price": qmoney(price),
                "quantity": qty,
                "total_price": qmoney(price * qty),
            }

    def __len__(self):
        return sum(int(i["quantity"]) for i in self.cart.values())

    @property
    def subtotal(self) -> Decimal:
        sub = sum(Decimal(i["price"]) * int(i["quantity"]) for i in self.cart.values())
        return qmoney(sub) if sub else Decimal("0.00")

    @property
    def shipping(self) -> Decimal:
        # ✅ W KOSZYKU ZAWSZE 0
        return Decimal("0.00")

    @property
    def grand_total(self) -> Decimal:
        # ✅ do zapłaty w koszyku = suma produktów
        return self.subtotal

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.session.modified = True
