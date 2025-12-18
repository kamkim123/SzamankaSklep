from django.contrib import admin
from import_export.admin import ExportMixin
from import_export import resources

from .models import NewsletterSubscriber


class NewsletterSubscriberResource(resources.ModelResource):
    class Meta:
        model = NewsletterSubscriber
        fields = ("email", "is_active", "created_at")
        export_order = ("email", "is_active", "created_at")


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = NewsletterSubscriberResource
    list_display = ("email", "is_active", "created_at")
    search_fields = ("email",)
    list_filter = ("is_active", "created_at")
