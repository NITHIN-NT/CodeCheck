"""
Django settings for review_dashboard project.

Adapted for deployment on Vercel (serverless functions + static files).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Detect Vercel build/runtime
IS_BUILD = os.environ.get("VERCEL_BUILD") == "1"
IS_VERCEL = os.environ.get("VERCEL") == "1"
CI = os.environ.get("CI") == "true"

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-placeholder")

# DEBUG on when explicit env var DEBUG=1, otherwise False by default in production
DEBUG = os.getenv("DEBUG", "0") == "1"

# Allowed hosts: include vercel host(s) if provided
_default_allowed = ["127.0.0.1", "localhost"]
_vercel_host = os.environ.get("VERCEL_URL")  # e.g. my-app-xyz.vercel.app
if _vercel_host:
    # Add both the bare host and the https form for CSRF/allowed hosts usage if needed
    _default_allowed.append(_vercel_host)
    # also allow subdomain .vercel.app
    _default_allowed.append(".vercel.app")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", ",".join(_default_allowed)).split(",")

# Application definition
if IS_BUILD:
    INSTALLED_APPS = [
        "django.contrib.staticfiles",
        "dashboard.apps.DashboardConfig",
    ]
else:
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "dashboard.apps.DashboardConfig",
    ]

# Minimal middleware during build to allow collectstatic without DB
if IS_BUILD:
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.middleware.common.CommonMiddleware",
    ]
else:
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

ROOT_URLCONF = "review_dashboard.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Use WSGI for Vercel serverless entrypoint (you have wsgi.py)
WSGI_APPLICATION = "review_dashboard.wsgi.application"

# Database
# During build, we don't need an actual DB for collectstatic. Keep your monkey-patch.
if IS_BUILD:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

    # Prevent accidental DB access during build (collectstatic)
    try:
        import django.db

        original_get_connection = django.db.connections.__getitem__

        def patched_get_connection(alias):
            if alias == "default":
                raise django.db.utils.DatabaseError("Database not available during build")
            return original_get_connection(alias)

        django.db.connections.__getitem__ = patched_get_connection
    except Exception:
        # If Django not yet imported or patch fails, ignore during build.
        pass
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

    # In Vercel runtime use writable /tmp path for sqlite (serverless)
    if IS_VERCEL or CI:
        DATABASES["default"]["NAME"] = "/tmp/db.sqlite3"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "dashboard", "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# WhiteNoise for static serving
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True

# Security: when running on Vercel, ensure secure headers are respected if behind proxy
# Tell Django the real scheme when Vercel forwards HTTPS (Vercel does TLS termination)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Redirect to HTTPS in production on Vercel unless DEBUG explicitly enabled
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "1") == "1" and not DEBUG

# CSRF trusted origins - add Vercel URL if provided
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
if _vercel_host:
    # Django requires scheme included (https://...)
    vercel_origin = f"https://{_vercel_host}"
    if vercel_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(vercel_origin)

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Any 3rd-party API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Helpful debug printing when DEBUG=1 (optional)
if DEBUG:
    # Ensure that at least '127.0.0.1' and 'localhost' are allowed
    if "127.0.0.1" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append("127.0.0.1")
