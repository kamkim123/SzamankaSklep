from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from products.models import Product
from .models import Coupon

MONEY_Q = Decimal("0.01")

def qmoney(x: Decimal) -> Decimal:
    return x.quantize(MONEY_Q, rounding=ROUND_HALF_UP)

COUPON_SESSION_KEY = "cart_coupon_code"


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
        # ✅ W KOSZYKU ZAWSZE 0 (dostawa liczona dopiero w checkout)
        return Decimal("0.00")

    # =========================
    # KUPON / RABAT
    # =========================
    @property
    def coupon_code(self) -> str:
        return self.session.get(COUPON_SESSION_KEY, "")

    @property
    def coupon(self):
        code = self.coupon_code
        if not code:
            return None
        try:
            c = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return None
        return c if c.is_valid_now() else None

    def apply_coupon(self, code: str) -> tuple[bool, str]:
        code = (code or "").strip()
        if not code:
            self.remove_coupon()
            return True, "Usunięto kod rabatowy."

        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            return False, "Nieprawidłowy kod rabatowy."

        if not coupon.is_valid_now():
            return False, "Ten kod rabatowy jest nieaktywny lub wygasł."

        self.session[COUPON_SESSION_KEY] = coupon.code.upper()
        self.session.modified = True
        return True, f"Zastosowano kod: {coupon.code.upper()} (-{coupon.percent}%)."

    def remove_coupon(self):
        self.session.pop(COUPON_SESSION_KEY, None)
        self.session.modified = True

    @property
    def discount_amount(self) -> Decimal:
        c = self.coupon
        if not c or not c.percent:
            return Decimal("0.00")
        disc = (self.subtotal * Decimal(c.percent) / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return min(disc, self.subtotal)  # rabat nie może przekroczyć subtotal

    @property
    def grand_total(self) -> Decimal:
        # ✅ subtotal + shipping - discount (shipping u Ciebie = 0 w koszyku)
        total = self.subtotal + self.shipping - self.discount_amount
        if total < 0:
            total = Decimal("0.00")
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def clear(self):
        self.session.pop(settings.CART_SESSION_ID, None)
        self.remove_coupon()  # ✅ wyczyść też kupon
        self.session.modified = True
