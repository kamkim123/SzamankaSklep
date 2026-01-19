import dj_database_url
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ===== Podstawy produkcyjne =====
DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "dber74gf7%&DFcwcwdq!")
ALLOWED_HOSTS = [
    "szamankasklep.pl",
    "www.szamankasklep.pl",
    "api.szamanka.pl",             # Twoja subdomena API
    "szamankasklep.onrender.com",      # chwilowo adres z Render, podmienisz po deployu
    "localhost", "127.0.0.1"
]

import os


if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:

    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_USE_SSL = False

    EMAIL_HOST_USER = "szamankasklep@gmail.com"
    EMAIL_HOST_PASSWORD = "cghsmpbwjbxmzvnb"

    DEFAULT_FROM_EMAIL = "szamankasklep@gmail.com"
    SERVER_EMAIL = "szamankasklep@gmail.com"

USE_X_FORWARDED_HOST = True


import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())


INSTALLED_APPS = [
    "newsletter.apps.NewsletterConfig",
    "users.apps.UsersConfig",
    "orders.apps.OrdersConfig",
    "products.apps.ProductsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "import_export",
    "corsheaders",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
]



MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",       # ⬅️ przenieś tu
    "corsheaders.middleware.CorsMiddleware",            # ⬅️ przed CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

WHITENOISE_USE_FINDERS = True

CORS_ALLOWED_ORIGINS = [
    "https://szamankasklep.pl",
    "https://www.szamankasklep.pl",
]

ROOT_URLCONF = "Szamanka.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],   # albo [] jeśli trzymasz w appce
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",     # opcjonalnie
                "django.contrib.auth.context_processors.auth",   # <— ważne
                "django.contrib.messages.context_processors.messages",  # <— ważne
                "Szamanka.context_processors.categories_ctx",
                "orders.context_processors.cart_counts",
                "products.context_processors.navbar_categories",

            ],
        },
    },
]

WSGI_APPLICATION = "Szamanka.wsgi.application"

DJANGO_DB_PATH = os.getenv("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))

DATABASES = {
    "default": dj_database_url.parse(
        "postgresql://kamyk3226:iTwmja0Urf3bGjj1ZQIJvzSrAlnK2gMj@"
        "dpg-d3jnr43ipnbc73clhnng-a.frankfurt-postgres.render.com/szamanka",
        conn_max_age=300,         # 5 min – połączenia są re-używane
        ssl_require=True,
    )
}

DATABASES["default"]["OPTIONS"] = {
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 5,
    "connect_timeout": 15,
    # na czas importu — dłuższe zapytania:
    "options": "-c statement_timeout=0",  # albo np. 600000 (10 min)
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",      # standardowy
    "allauth.account.auth_backends.AuthenticationBackend",  # allauth
]

CSRF_COOKIE_NAME = "csrftoken"

SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"


LOGIN_URL = '/u/login/'
LOGIN_REDIRECT_URL = "home"   # albo inny istniejący widok
LOGOUT_REDIRECT_URL = "home"

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False

ACCOUNT_SIGNUP_FIELDS = {'email*'}

ACCOUNT_ADAPTER = "users.adapter.MyAccountAdapter"

ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300


# Lokalizacja
LANGUAGE_CODE = "pl"           # było en-us
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""

ACCOUNT_FORMS = {
    "signup": "users.forms.MySignupForm",
}


# Statyczne i media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===== Bezpieczeństwo (włączysz po HTTPS) =====
#SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
CSRF_TRUSTED_ORIGINS = ["https://szamankasklep.pl", "https://www.szamankasklep.pl",  "http://127.0.0.1:8000",  # Lokalny adres
    "http://localhost:8000"]


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

CART_SESSION_ID = "cart"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 20000


LOGGING = {
    "version": 1,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "allauth": {"handlers": ["console"], "level": "DEBUG"},
        "django.request": {"handlers": ["console"], "level": "ERROR"},
    },
}

ACCOUNT_EMAIL_REQUIRED = True


DATABASES["default"]["CONN_MAX_AGE"] = 60  # lub nawet 0 na czas diagnozy
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True  # Django 4.1+
DATABASES["default"]["OPTIONS"].update({
    "keepalives": 1, "keepalives_idle": 30, "keepalives_interval": 10, "keepalives_count": 5,
})


# settings.py

EPAKA_CLIENT_ID = "8f6838db44fbd3149716f3c3a214c183"
EPAKA_CLIENT_SECRET = "b117c80f5dbaa46ad6a95315ca191dcc321f07b090cf852821ce6c4add501b6c"

EPAKA_AUTHORIZE_URL = "https://epaka.pl/auth/oauth/autorizatize"
EPAKA_TOKEN_URL = "https://api.epaka.pl/oauth/token"
EPAKA_API_BASE_URL = "https://api.epaka.pl"

# URL dokładnie taki sam, jak skonfigurowany w menadżerze aplikacji na epaka.pl
EPAKA_REDIRECT_URI = "https://www.szamankasklep.pl/epaka/callback/"

# INPOST – weź id z /v1/couriers (np. kurier / paczkomaty)
EPAKA_COURIER_INPOST = 12
EPAKA_COURIER_DPD = 1
EPAKA_COURIER_DHL = 8
EPAKA_LOCKER_INPOST = 6


SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 dni jako domyślna "długa" sesja




P24_SANDBOX = os.getenv("P24_SANDBOX", "1") == "1"

P24_MERCHANT_ID = int(os.getenv("P24_MERCHANT_ID", "0"))
P24_POS_ID = int(os.getenv("P24_POS_ID", str(P24_MERCHANT_ID)))  # często to samo
P24_CRC = os.getenv("P24_CRC", "")
P24_API_KEY = os.getenv("P24_API_KEY", "")  # do basicAuth (reports key)


if P24_SANDBOX:
    P24_API_BASE = "https://sandbox.przelewy24.pl/api/v1"
    P24_TRN_BASE = "https://sandbox.przelewy24.pl/trnRequest"
else:
    P24_API_BASE = "https://secure.przelewy24.pl/api/v1"
    P24_TRN_BASE = "https://secure.przelewy24.pl/trnRequest"


SITE_NAME = "SzamankaSklep"
COMPANY_NAME = "Twoja Firma Sp. z o.o."
COMPANY_IBAN = "PL12 3456 7890 1234 5678 9012 3456"
