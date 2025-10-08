import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# ===== Podstawy produkcyjne =====
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "dber74gf7%&DFcwcwdq!")
ALLOWED_HOSTS = [
    "api.szamanka.pl",             # Twoja subdomena API
    "https://szamankasklep.onrender.com",      # chwilowo adres z Render, podmienisz po deployu
    "localhost", "127.0.0.1"
]


INSTALLED_APPS = [
    "users.apps.UsersConfig",
    "orders.apps.OrdersConfig",
    "products.apps.ProductsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "import_export",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
            ],
        },
    },
]

WSGI_APPLICATION = "Szamanka.wsgi.application"

DJANGO_DB_PATH = os.getenv("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3"))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DJANGO_DB_PATH,
        "OPTIONS": {"timeout": 10}
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

CSRF_COOKIE_NAME = "csrftoken"


LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "home"   # albo inny istniejący widok
LOGOUT_REDIRECT_URL = "home"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"



# Lokalizacja
LANGUAGE_CODE = "pl"           # było en-us
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True

# Statyczne i media
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media"))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ===== Bezpieczeństwo (włączysz po HTTPS) =====
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
CSRF_TRUSTED_ORIGINS = ["https://szamankasklep.pl", "https://www.szamankasklep.pl"]
