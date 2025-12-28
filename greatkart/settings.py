"""
Cleaned Settings for Greatkart Project
Suitable for: Render / Railway / PythonAnywhere
Cloudinary for media & WhiteNoise for static
"""

from pathlib import Path
import os
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------------

# Fixed: Using "SECRET_KEY" as the env var name, with the user's key as default
SECRET_KEY = config("SECRET_KEY", default="FYz9fYz2fMIFshtXUQ7wXTJ5QQU")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

# Render specific configuration
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# -----------------------------------------------------------------------------------
# APPLICATIONS
# -----------------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps
    "category",
    "accounts",
    "store",
    "carts",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <=== for static on production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "greatkart.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["ecommerce/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "category.context_processors.menu_links",
                "carts.context_processors.counter",
            ],
        },
    },
]

WSGI_APPLICATION = "greatkart.wsgi.application"


# -----------------------------------------------------------------------------------
# DATABASE — works on local + Render/Railway/PythonAnywhere
# -----------------------------------------------------------------------------------

if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(default=os.environ["DATABASE_URL"])}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# -----------------------------------------------------------------------------------
# STORAGE CONFIGURATION
# -----------------------------------------------------------------------------------

# === CLOUDINARY for user-uploaded images ===
# Fixed: Using "CLOUDINARY_URL" as env var name. 
# Added default from your input, removing the <> placeholders which would cause errors.
CLOUDINARY_URL = config("CLOUDINARY_URL", default="cloudinary://826254745148537:FYz9fYz2fMIFshtXUQ7wXTJ5QQU@dc6yqjtm9")

if CLOUDINARY_URL:
    # CLOUDINARY_URL is handled automatically by the library if set in env
    pass

# Configure django-cloudinary-storage
# Fixed: Keys should be env var names, values provided as defaults
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default="dc6yqjtm9"),
    "API_KEY": config("CLOUDINARY_API_KEY", default="826254745148537"),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default="FYz9fYz2fMIFshtXUQ7wXTJ5QQU"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# === STATIC FILES ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "greatkart/static"]

# Use WhiteNoise for static files in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# === Media ===
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# -----------------------------------------------------------------------------------
# AUTH, LANGUAGE, TIME, MESSAGES
# -----------------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.Account"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
