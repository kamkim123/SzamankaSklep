# shop/admin.py
from django.contrib import admin
from decimal import Decimal, InvalidOperation
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import CharWidget, IntegerWidget, DecimalWidget
from .models import Product

# ---- WIDGETY POMOCNICZE ----
class VATWidget(CharWidget):
    """Zwraca '0'/'5'/'8'/'23' (string) zgodnie z choices."""
    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ""):
            return "8"
        s = str(value).strip().replace("%", "").replace(",", ".")
        try:
            v = int(float(s))
        except Exception:
            return "8"
        return str(v) if str(v) in {"0", "5", "8", "23"} else "8"

class ProductTypeWidget(CharWidget):
    MAP = {
        "Artykuły spożywcze": Product.ProductType.SPOZYWCZE,
        "Suplementy diety": Product.ProductType.SUPLEMENTY,
        "Kosmetyki do włosów": Product.ProductType.KOSMETYKI_WLOSY,
        "Kosmetyki do ciała": Product.ProductType.KOSMETYKI_CIALO,
        "Kosmetyki do twarzy": Product.ProductType.KOSMETYKI_TWARZ,
        "Mydła": Product.ProductType.KOSMETYKI_CIALO,
        "Ziola i herbaty": Product.ProductType.ZIOLA,
        "Oleje, soki, syropy": Product.ProductType.SPOZYWCZE,
        "Maści": Product.ProductType.MASCI,
        "ziola": Product.ProductType.ZIOLA,
        "zioła": Product.ProductType.ZIOLA,
        "Inne": Product.ProductType.INNE,
        "spozywcze": Product.ProductType.SPOZYWCZE,
        "suplementy": Product.ProductType.SUPLEMENTY,
        "kosmetyki do włosów": Product.ProductType.KOSMETYKI_WLOSY,
        "kosmetyki do ciała": Product.ProductType.KOSMETYKI_CIALO,
        "kosmetyki do twarzy": Product.ProductType.KOSMETYKI_TWARZ,
        "masci": Product.ProductType.MASCI,
        "inne": Product.ProductType.INNE,
    }
    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ""):
            return Product.ProductType.SPOZYWCZE
        return self.MAP.get(str(value).strip(), Product.ProductType.SPOZYWCZE)

class SafeIntegerFromMixedWidget(IntegerWidget):
    """Dla 'Kod': wyciąga cyfry z np. 'A-123/blue' → 123. Dla pustych: None."""
    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ""):
            return None
        s = str(value)
        digits = "".join(ch for ch in s if ch.isdigit())
        return int(digits) if digits else None

class StockWidget(IntegerWidget):
    """Stan: akceptuje 10, '10', '10,0', '10.0' → int."""
    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ""):
            return 0
        try:
            return int(float(str(value).replace(",", ".")))
        except Exception:
            return 0

class DecimalCommaWidget(DecimalWidget):
    """Cena: akceptuje przecinek/kropkę. Puste → 0.00 (bo pole jest required)."""
    def clean(self, value, row=None, *args, **kwargs):
        if value in (None, ""):
            return Decimal("0.00")
        s = str(value).strip().replace(",", ".")
        try:
            return Decimal(s).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return Decimal("0.00")

class DefaultingCharWidget(CharWidget):
    """Zwraca default gdy wartość pusta."""
    def __init__(self, default="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default
    def clean(self, value, row=None, *args, **kwargs):
        v = super().clean(value, row=row, *args, **kwargs) or ""
        v = v.strip()
        return v if v else self.default

# ---- RESOURCE ----
class ProductResource(resources.ModelResource):
    # Polskie nagłówki w Excelu (kolumny opcjonalne są dozwolone)
    product_code = fields.Field(column_name="Kod paskowy", attribute="product_code", widget=SafeIntegerFromMixedWidget())
    product_name = fields.Field(column_name="Nazwa", attribute="product_name", widget=DefaultingCharWidget())
    product_stock = fields.Field(column_name="Stan", attribute="product_stock", widget=StockWidget())
    product_vat = fields.Field(column_name="Stawka VAT", attribute="product_vat", widget=VATWidget())
    price = fields.Field(column_name="Cena", attribute="price", widget=DecimalCommaWidget())
    product_category = fields.Field(column_name="Kategoria", attribute="product_category",
                                    widget=DefaultingCharWidget(default="Inne"))
    product_brand = fields.Field(column_name="Marka", attribute="product_brand", widget=DefaultingCharWidget(""))
    product_info = fields.Field(column_name="Opis", attribute="product_info", widget=DefaultingCharWidget(""))
    product_ingredients = fields.Field(column_name="Skład", attribute="product_ingredients",
                                       widget=DefaultingCharWidget(""))
    product_type = fields.Field(column_name="Grupy towarów Detal", attribute="product_type", widget=ProductTypeWidget())
    product_weight = fields.Field(column_name="waga", attribute="product_weight", widget=DefaultingCharWidget(""))
    product_image = fields.Field(column_name="url_zdjecia", attribute="product_image", widget=DefaultingCharWidget(""))


    class Meta:
        model = Product
        # import_id_fields jest wymagane, ale i tak nadpisujemy get_instance()
        import_id_fields = ("product_code",)
        fields = (
            "product_code",
            "product_name",
            "price",
            "product_stock",
            "product_vat",
            "product_category",
            "product_brand",
            "product_info",
            "product_ingredients",
            "product_type",
            "product_image",
            "product_weight",
        )
        skip_unchanged = True
        report_skipped = True

    # Idempotencja: najpierw po product_code (jeśli jest), inaczej po product_name
    def get_instance(self, instance_loader, row, *args, **kwargs):
        code_raw = row.get("Kod")
        code = SafeIntegerFromMixedWidget().clean(code_raw, row=row)
        if code is not None:
            try:
                return Product.objects.get(product_code=code)
            except Product.DoesNotExist:
                return None
        name = (row.get("Nazwa") or "").strip()
        if name:
            try:
                return Product.objects.get(product_name=name)
            except Product.DoesNotExist:
                return None
        return None




    # Bezpieczne przycinanie długich pól tekstowych
    def before_save_instance(self, instance, *args, **kwargs):
        if instance.product_info:
            instance.product_info = instance.product_info[:5000]
        if instance.product_ingredients:
            instance.product_ingredients = instance.product_ingredients[:1000]

        if not instance.product_category:
            instance.product_category = "Inne"
        if instance.product_vat not in {"0", "5", "8", "23"}:
            instance.product_vat = "8"
        if instance.product_type not in dict(Product.ProductType.choices):
            instance.product_type = Product.ProductType.SPOZYWCZE
        if instance.price is None:
            instance.price = Decimal("0.00")
        if instance.product_stock is None:
            instance.product_stock = 0

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = (
        "product_code",
        "product_name",
        "price",
        "promo_price",
        "product_stock",
        "product_vat",
        "product_category",
        "product_brand",
        "product_type",
        "is_bestseller",
        "is_promotion",  # Dodane pole do listy
        "is_new",  # Dodane pole do listy
        "is_popular",  # Dodane pole do listy
        "product_image",
        "product_weight",
    )
    search_fields = ("product_name", "product_brand", "product_category", "product_code")  # intowe product_code pomijamy w search_fields
    list_filter = ("product_vat", "product_type", "product_category", "product_brand")
    list_editable = ("is_bestseller", "is_promotion", "promo_price", "is_new", "is_popular",)

