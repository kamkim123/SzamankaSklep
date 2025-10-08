
from django.contrib import admin
from .models import Profile, Address

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "newsletter_opt_in", "created_at")
    search_fields = ("user__username", "user__email", "phone")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "is_default", "first_name", "last_name", "city", "postal_code")
    list_filter = ("type", "is_default", "country")
    search_fields = ("user__username", "user__email", "first_name", "last_name", "city", "postal_code")
