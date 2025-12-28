"""
Cleaned Settings for Greatkart Project
Suitable for: Render / Railway / PythonAnywhere
Cloudinary for media & WhiteNoise for static
"""
from decouple import config
from pathlib import Path
import os
import cloudinary
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------------

SECRET_KEY = config("SECRET_KEY", default="FYz9fYz2fMIFshtXUQ7wXTJ5QQU")
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["greatkart-ecommerce-zo01.onrender.com", "localhost", "127.0.0.1"]

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
    "whitenoise.middleware.WhiteNoiseMiddleware",  # for static files in production
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
# DATABASE
# -----------------------------------------------------------------------------------

if os.environ.get("DATABASE_URL"):
    import dj_database_url
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

CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL=cloudinary://<826254745148537>:<FYz9fYz2fMIFshtXUQ7wXTJ5QQU>@dc6yqjtm9")
if CLOUDINARY_URL:
    parsed_url = urlparse(CLOUDINARY_URL.replace("cloudinary://", "http://"))
    cloud_name = parsed_url.hostname
    api_key = parsed_url.username
    api_secret = parsed_url.password
    cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)
else:
    cloud_name = os.environ.get("dc6yqjtm9")
    api_key = os.environ.get("826254745148537")
    api_secret = os.environ.get("FYz9fYz2fMIFshtXUQ7wXTJ5QQU")
    if all([cloud_name, api_key, api_secret]):
        cloudinary.config(cloud_name=cloud_name, api_key=api_key, api_secret=api_secret)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": cloud_name,
    "API_KEY": api_key,
    "API_SECRET": api_secret,
    "prefix": "django_ecommerce",
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "greatkart/static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (fallback for local dev)
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
MESSAGE_TAGS = {messages.ERROR: "danger"}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
