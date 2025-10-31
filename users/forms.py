# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from .models import Profile, Address


User = get_user_model()

def unique_username_from_email(email: str) -> str:
    base = (email.split("@")[0] or "user")[:30]
    username = base
    n = 1
    while User.objects.filter(username=username).exists():
        suf = f"_{n}"
        username = base[:30 - len(suf)] + suf
        n += 1
    return username

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ten e-mail jest już używany.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)  # UserCreationForm zrobi set_password()
        email = self.cleaned_data["email"].strip().lower()
        user.email = email
        if not user.username:
            user.username = unique_username_from_email(email)
        # ukróć uprawnienia bezpieczeństwa-default
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class EmailAuthenticationForm(AuthenticationForm):
    # Pozostawiamy NAZWĘ pola "username" (LoginView tego wymaga),
    # ale zmieniamy label + widget na e-mail.
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean(self):
        # W tym formularzu "username" = email użytkownika
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            try:
                user_obj = User.objects.get(email__iexact=email.strip().lower())
                real_username = user_obj.get_username()
            except User.DoesNotExist:
                real_username = None

            self.user_cache = authenticate(self.request, username=real_username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class MySignupForm(SignupForm):
    first_name = forms.CharField(label="Imię", max_length=30, required=False)
    terms_accepted = forms.BooleanField(label="Akceptuję regulamin", required=True)

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.save()
        # jeśli musisz coś zapisać poza userem — zrób to tutaj
        return user





from django import forms
from django.contrib.auth import get_user_model



class UserUpdateForm(forms.ModelForm):
    class Meta:
            model = User
            fields = ["first_name", "last_name", "email"]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
            model = Profile
            fields = ["phone"]

class AddressForm(forms.ModelForm):
    class Meta:
            model = Address
            fields = ["address_line_1", "city", "postal_code"]