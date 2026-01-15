import datetime

from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError


def was_published_recently(self):
    now = timezone.now()
    return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Product(models.Model):
    class ProductType(models.TextChoices):
        SPOZYWCZE = "spozywcze", "Spożywcze"
        SUPLEMENTY = "suplementy", "Suplementy"
        KOSMETYKI_WLOSY  = "kosmetyki do włosów", "Kosmetyki do włosów"
        KOSMETYKI_CIALO = "kosmetyki do ciała", "Kosmetyki do ciała"
        KOSMETYKI_TWARZ = "kosmetyki do twarzy", "Kosmetyki do twarzy"
        MASCI = "masci", "Maści"
        ZIOLA = "ziola", "Zioła"
        INNE = "inne", "Inne"

    product_name = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    product_info = models.TextField(max_length=5000, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.CharField(max_length=50, db_index=True)
    product_brand = models.CharField(max_length=50, blank=True, db_index=True)
    product_code = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    product_stock = models.IntegerField(default=0)
    product_vat = models.CharField(
        max_length=10,
        choices=[("0","0%"), ("5","5%"), ("8","8%"), ("23","23%")],
        default="8"
    )

    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.SPOZYWCZE
    )
    product_ingredients = models.TextField(max_length=1000, blank=True)
    product_weight = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    # models.py
    product_image = models.URLField(null=True, blank=True,
                                    default='static/products/images/default-image.png')

    is_bestseller = models.BooleanField(default=False)
    is_promotion = models.BooleanField(default=False)  # Pole dla promocji
    is_new = models.BooleanField(default=False)  # Pole dla nowości
    is_popular = models.BooleanField(default=False)  # Pole dla popularności

    def __str__(self):
        return self.product_name


    price = models.DecimalField(max_digits=10, decimal_places=2)

    # DODAJ:
    promo_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True
    )

    is_promotion = models.BooleanField(default=False)

    def clean(self):
        # walidacja spójności
        if self.is_promotion:
            if self.promo_price is None:
                raise ValidationError({"promo_price": "Ustaw cenę promocyjną albo wyłącz promocję."})
            if self.promo_price >= self.price:
                raise ValidationError({"promo_price": "Cena promocyjna musi być niższa od ceny podstawowej."})

    @property
    def has_promo(self):
        return self.is_promotion and self.promo_price is not None and self.promo_price < self.price

    @property
    def final_price(self):
        return self.promo_price if self.has_promo else self.price

    @property
    def discount_percent(self) -> int:
        if not self.has_promo:
            return 0
        # zaokrąglamy do int
        return int((Decimal("1") - (self.promo_price / self.price)) * 100)

    def __str__(self):
        return self.product_name

    @property
    def effective_price(self) -> Decimal:
        """Cena, którą faktycznie ma zapłacić klient."""
        promo = getattr(self, "promo_price", None)
        if self.is_promotion and promo not in (None, ""):
            return promo
        return self.price