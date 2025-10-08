# orders/forms.py
from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name", "last_name", "email", "phone",
            "address", "postal_code", "city",
            "payment_method", "notes",
        ]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}
