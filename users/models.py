from django.db import models

# users/models.py
from django.conf import settings
from django.db import models
import uuid


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", primary_key=True,)
    phone = models.CharField(max_length=30, blank=True)
    newsletter_opt_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Profil: {self.user.get_username()}"

class Address(models.Model):
    SHIPPING = "shipping"
    BILLING = "billing"
    TYPE_CHOICES = [(SHIPPING, "Wysyłkowy"), (BILLING, "Rozliczeniowy")]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="addresses", default="", blank=True)
    address_line_1 = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=120, default="", blank=True)
    postal_code = models.CharField(max_length=20, default="", blank=True)

    def __str__(self):
        return f"{self.address_line_1}, {self.city}"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=SHIPPING)

    first_name = models.CharField(max_length=60)
    last_name  = models.CharField(max_length=60)
    phone      = models.CharField(max_length=30, blank=True)

    address     = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=10)
    city        = models.CharField(max_length=60)
    country     = models.CharField(max_length=2, default="PL")  # ISO 2

    is_default = models.BooleanField(default=False)  # czy domyślny dla danego type

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "type", "last_name"]
        indexes = [
            models.Index(fields=["user", "type"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self):
        return f"{self.get_type_display()} {self.first_name} {self.last_name}, {self.city}"


from django.conf import settings
from django.db import models
from products.models import Product  # Import produktu z aplikacji 'produkty'

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user} ❤ {self.product}"

