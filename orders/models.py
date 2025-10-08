
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

    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="cart_items")

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product} x {self.quantity}"


# orders/models.py


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

    # flaga: czy zdjęto już stan magazynowy (żeby nie zdjąć 2x)
    stock_debited = models.BooleanField(default=False)

    # stan i płatność
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_TRANSFER)
    paid            = models.BooleanField(default=False)

    # koszty
    shipping_cost   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    notes           = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
                check=Q(email__isnull=False) & ~Q(email=""),
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
        return (self.items_total + self.shipping_cost).quantize(Decimal("0.01"))


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="order_items")

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









