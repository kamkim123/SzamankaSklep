
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

class Cart(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)

    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        who = self.user or self.session_key or f"id={self.pk}"
        return f"Cart({who})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="cart_items")

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product} x {self.quantity}"


# orders/models.py
#poprawione

class Order(models.Model):
    STATUS_NEW = "new"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_NEW, "Nowe"),
        (STATUS_PAID, "Opłacone"),
        (STATUS_SHIPPED, "Wysłane"),
        (STATUS_CANCELLED, "Anulowane"),
    ]

    PAYMENT_TRANSFER = "transfer"
    PAYMENT_COD = "cod"        # za pobraniem
    PAYMENT_ONLINE = "online"  # np. PayU/Przelewy24
    PAYMENT_CHOICES = [
        (PAYMENT_TRANSFER, "Przelew"),
        (PAYMENT_COD, "Za pobraniem"),
        (PAYMENT_ONLINE, "Płatność online"),
    ]

    SHIPPING_INPOST_COURIER = "inpost_courier"
    SHIPPING_DPD_COURIER = "dpd_courier"
    SHIPPING_INPOST_LOCKER = "inpost_locker"
    SHIPPING_PICKUP = "pickup"

    SHIPPING_CHOICES = [
        (SHIPPING_INPOST_COURIER, "InPost Courier"),
        (SHIPPING_DPD_COURIER, "DPD Courier"),
        (SHIPPING_INPOST_LOCKER, "InPost Locker"),
        (SHIPPING_PICKUP, "Pickup"),
    ]

    # orders/models.py (w klasie Order)

    PACKAGE_NONE = ""
    PACKAGE_1 = "1"
    PACKAGE_2 = "2"
    PACKAGE_3 = "3"
    PACKAGE_4 = "4"
    PACKAGE_5 = "5"

    PACKAGE_CHOICES = [
        (PACKAGE_NONE, "— wybierz —"),
        (PACKAGE_1, "1) 17×20×20 cm (do 1 kg)"),
        (PACKAGE_2, "2) 25×20×20 cm (do 4 kg)"),
        (PACKAGE_3, "3) 35×25×15 cm (do 6 kg)"),
        (PACKAGE_4, "4) 35×35×30 cm (do 10 kg)"),
        (PACKAGE_5, "5) 45×45×45 cm (do 15 kg)"),
    ]

    package_size = models.CharField(
        max_length=2,
        choices=PACKAGE_CHOICES,
        default=PACKAGE_NONE,
        blank=True,
    )

    epaka_sent_at = models.DateTimeField(null=True, blank=True)
    epaka_last_error = models.TextField(blank=True)

    # NOWE POLE
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_CHOICES,
        default=SHIPPING_INPOST_COURIER,
    )

    inpost_locker_code = models.CharField(
        max_length=32,
        blank=True,
        help_text="Kod paczkomatu InPost (np. WAW01N)",
    )

    # kto składa (opcjonalnie user lub gość)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="orders"
    )

    # dane do wysyłki / kontakt
    first_name = models.CharField(max_length=60)
    last_name  = models.CharField(max_length=60)
    email      = models.EmailField()
    phone      = models.CharField(max_length=30, blank=True)
    address    = models.CharField(max_length=200)
    postal_code= models.CharField(max_length=10)
    city       = models.CharField(max_length=60)

    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=60, blank=True)

    epaka_order_id = models.CharField(max_length=60, blank=True)
    epaka_label_number = models.CharField(max_length=60, blank=True)

    # flaga: czy zdjęto już stan magazynowy (żeby nie zdjąć 2x)
    stock_debited = models.BooleanField(default=False)

    # stan i płatność
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_TRANSFER)
    paid            = models.BooleanField(default=False)

    # koszty
    shipping_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # ✅ KUPON / RABAT
    coupon_code = models.CharField(max_length=40, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    notes           = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    p24_session_id = models.CharField(max_length=80, blank=True)
    p24_token = models.CharField(max_length=80, blank=True)
    p24_order_id = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["paid"]),
        ]
        constraints = [
            # przynajmniej email + (user lub cokolwiek, ale email i tak jest wymagany przez pole)
            models.CheckConstraint(
                condition=Q(email__isnull=False) & ~Q(email=""),
                name="order_email_required",
            ),
        ]

    def __str__(self):
        return f"Order #{self.pk} – {self.last_name}"

    @property
    def items_total(self) -> Decimal:
        # suma pozycji (bez dostawy)
        return sum((it.unit_price * it.quantity for it in self.items.all()), Decimal("0.00"))

    @property
    def total_to_pay(self) -> Decimal:
        total = self.items_total + self.shipping_cost - (self.discount_amount or Decimal("0.00"))
        if total < 0:
            total = Decimal("0.00")
        return total.quantize(Decimal("0.01"))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="order_items")

    # snapshot ceny z chwili dodania do zamówienia
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    quantity   = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # (opcjonalnie) snapshot nazwy, jeśli chcesz mieć niezależność od późniejszych zmian
    product_name = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("order", "product")  # jedna pozycja danego produktu w zamówieniu

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return (self.unit_price * self.quantity).quantize(Decimal("0.01"))


from django.utils import timezone

class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    percent = models.PositiveIntegerField(default=0, help_text="0-100 (%)")
    active = models.BooleanField(default=True)

    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.code} (-{self.percent}%)"

    def is_valid_now(self) -> bool:
        if not self.active:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True



class EpakaToken(models.Model):
    access_token = models.TextField()
    expires_at = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_valid(cls):
        tok = cls.objects.order_by("-updated_at").first()
        if tok and tok.expires_at > timezone.now() + timezone.timedelta(seconds=30):
            return tok.access_token
        return None







