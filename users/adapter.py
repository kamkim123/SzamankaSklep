from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return str(resolve_url("home"))

    # Przykład: blokada rejestracji na konkretne domeny e-mail:
    # def is_open_for_signup(self, request):
    #     return True  # lub warunek
