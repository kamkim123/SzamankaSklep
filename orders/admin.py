# orders/admin.py
from django.contrib import admin, messages
from django.utils import timezone
from .models import Order, OrderItem

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
        "short_notes",
    )
    list_filter = ("status", "paid", "created_at", "payment_method", "shipped_at")
    search_fields = ("id", "last_name", "email", "address", "city", "tracking_number", "notes")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at", "items_total_display", "total_to_pay_display")

    actions = ["mark_paid", "mark_shipped", "mark_cancelled"]

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
