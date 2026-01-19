# orders/admin.py
from django.contrib import admin, messages
from django.utils import timezone
from .models import Order, OrderItem
from django.utils.html import format_html
from django.urls import reverse
from django.db import transaction
from .epaka import create_epaka_order
from .epaka_auth import get_epaka_access_token


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "product_name", "unit_price", "quantity", "line_total_display")
    readonly_fields = ("line_total_display",)

    def line_total_display(self, obj):
        return f"{obj.line_total:.2f} zł" if obj.pk else "-"
    line_total_display.short_description = "Suma pozycji"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id", "created_at", "last_name", "email",
        "status_label", "shipped_at",
        "paid", "items_total_display", "total_to_pay_display",
        "short_notes", "package_size", "epaka_sent_at", "epaka_last_error",
        "epaka_label_link",
    )
    list_filter = ("status", "paid", "created_at", "payment_method", "shipped_at")
    search_fields = ("id", "last_name", "email", "address", "city", "tracking_number", "notes")
    inlines = [OrderItemInline]
    readonly_fields = (
        "created_at", "updated_at",
        "items_total_display", "total_to_pay_display",
        "epaka_last_error", "epaka_sent_at", "epaka_order_id",
    )

    actions = ["mark_paid", "mark_shipped", "mark_cancelled", "send_to_epaka"]


    # === Kolumny/etykiety ===
    def status_label(self, obj):
        return obj.get_status_display()
    status_label.short_description = "Status"

    def short_notes(self, obj):
        if not obj.notes:
            return "—"
        return (obj.notes[:40] + "…") if len(obj.notes) > 40 else obj.notes
    short_notes.short_description = "Notatki"
    short_notes.admin_order_field = "notes"

    def items_total_display(self, obj):
        return f"{obj.items_total:.2f} zł"
    items_total_display.short_description = "Suma pozycji"

    def total_to_pay_display(self, obj):
        return f"{obj.total_to_pay:.2f} zł"
    total_to_pay_display.short_description = "Do zapłaty"

    def epaka_label_link(self, obj):
        if not obj.epaka_order_id:
            return "—"
        url = reverse("orders:epaka_label", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Pobierz etykietę</a>', url)

    epaka_label_link.short_description = "Etykieta Epaka"

    # === Akcje ===
    @admin.action(description="Oznacz jako opłacone (zdejmij stan)")
    def mark_paid(self, request, queryset):
        updated = 0
        for order in queryset.prefetch_related("items__product"):
            if order.paid:
                continue
            order.paid = True
            order.status = Order.STATUS_PAID
            order.paid_at = timezone.now()

            if not order.stock_debited:
                for it in order.items.all():
                    if hasattr(it.product, "stock") and it.product.stock is not None:
                        it.product.stock = max(0, it.product.stock - it.quantity)
                        it.product.save(update_fields=["stock"])
                order.stock_debited = True

            order.save(update_fields=["paid", "status", "paid_at", "stock_debited", "updated_at"])
            updated += 1
        self.message_user(request, f"Oznaczono jako opłacone: {updated}", level=messages.SUCCESS)

    @admin.action(description="Oznacz jako wysłane")
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_SHIPPED, shipped_at=timezone.now())
        self.message_user(request, f"Oznaczono jako wysłane: {updated}", level=messages.SUCCESS)

    @admin.action(description="Anuluj zamówienie (oddaj stan, jeśli zdjęty)")
    def mark_cancelled(self, request, queryset):
        updated = 0
        for order in queryset.prefetch_related("items__product"):
            if order.status == Order.STATUS_CANCELLED:
                continue
            if order.stock_debited:
                for it in order.items.all():
                    if hasattr(it.product, "stock") and it.product.stock is not None:
                        it.product.stock = it.product.stock + it.quantity
                        it.product.save(update_fields=["stock"])
                order.stock_debited = False
            order.status = Order.STATUS_CANCELLED
            order.save(update_fields=["status", "stock_debited", "updated_at"])
            updated += 1
        self.message_user(request, f"Anulowano: {updated}", level=messages.WARNING)


    @admin.action(description="Wyślij do ePaki (wymaga: opłacone + rozmiar paczki)")
    def send_to_epaka(self, request, queryset):
        token = get_epaka_access_token()
        if not token:
            self.message_user(request, "Nie udało się pobrać tokena ePaki.", level=messages.ERROR)
            return

        sent = 0
        skipped = 0

        for order in queryset:
            # 1) tylko opłacone
            if not order.paid or order.status != Order.STATUS_PAID:
                skipped += 1
                continue

            # 2) nie wysyłaj drugi raz
            if order.epaka_order_id:
                skipped += 1
                continue

            # 3) musi być rozmiar
            if not order.package_size:
                order.epaka_last_error = "Brak package_size – wybierz rozmiar 1–5 w adminie."
                order.notes = (order.notes or "") + f"\n[EPAKA] ERROR: {order.epaka_last_error}\n"
                order.save(update_fields=["epaka_last_error", "notes"])
                skipped += 1
                continue

            # 4) wysyłka do ePaki
            with transaction.atomic():
                data = create_epaka_order(order, token)
                if not data:
                    skipped += 1
                    continue

                # ✅ sukces: czyścimy błąd i zapisujemy datę wysłania do ePaki
                order.epaka_last_error = ""
                order.epaka_sent_at = timezone.now()
                order.save(update_fields=["epaka_sent_at", "epaka_last_error", "updated_at"])

                sent += 1

        self.message_user(
            request,
            f"Wysłano do ePaki: {sent}, pominięto: {skipped}",
            level=messages.SUCCESS if sent else messages.WARNING
        )

from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "percent", "active", "valid_from", "valid_to")
    search_fields = ("code",)
    list_filter = ("active",)
