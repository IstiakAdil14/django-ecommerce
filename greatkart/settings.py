"""
Cleaned Settings for Greatkart Project
Suitable for: Render / Railway / PythonAnywhere
Cloudinary for media & WhiteNoise for static
"""
from decouple import config
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent


# -----------------------------------------------------------------------------------
# SECURITY
# -----------------------------------------------------------------------------------

SECRET_KEY = "FYz9fYz2fMIFshtXUQ7wXTJ5QQU"
DEBUG = True  # set True only locally

ALLOWED_HOSTS = [
    ALLOWED_HOSTS = ['greatkart-ecommerce-zo01.onrender.com', 'localhost', '127.0.0.1']
]


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

if os.environ.get("DATABASE_URL"):  # Render & Railway auto inject
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

# === CLOUDINARY for user-uploaded images ===
import cloudinary
from urllib.parse import urlparse

# Configure Cloudinary using environment variables
# Supports both CLOUDINARY_URL (single connection string) and individual vars
CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL=cloudinary://<826254745148537>:<FYz9fYz2fMIFshtXUQ7wXTJ5QQU>@dc6yqjtm9")

# Parse and configure Cloudinary SDK (for migration scripts and direct usage)
if CLOUDINARY_URL:
    # Parse CLOUDINARY_URL: cloudinary://api_key:api_secret@cloud_name
    try:
        # Replace cloudinary:// with http:// for parsing
        parsed_url = urlparse(CLOUDINARY_URL.replace("cloudinary://", "http://"))
        cloud_name = parsed_url.hostname
        api_key = parsed_url.username
        api_secret = parsed_url.password
        
        if cloud_name and api_key and api_secret:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
            )
    except Exception as e:
        # Fallback: let cloudinary.config() try to read from env var directly
        cloudinary.config()
else:
    # Otherwise, use individual environment variables
    cloud_name = os.environ.get(" dc6yqjtm9")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")
    if all([cloud_name, api_key, api_secret]):
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )

# Configure django-cloudinary-storage
# It will automatically read from CLOUDINARY_URL or individual env vars
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("dc6yqjtm9"),
    "API_KEY": os.environ.get("826254745148537"),
    "API_SECRET": os.environ.get("FYz9fYz2fMIFshtXUQ7wXTJ5QQU"),
}

# Set a prefix/folder for uploaded files in Cloudinary
CLOUDINARY_STORAGE["prefix"] = "django_ecommerce"

# Use Cloudinary storage for media files
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# === STATIC FILES ===
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "greatkart/static"]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# === Media (Cloudinary handles the path) ===
# CloudinaryStorage will return full URLs, but we keep MEDIA_URL for local dev fallback
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"  # Fallback for local dev and migration scripts


# -----------------------------------------------------------------------------------
# AUTH, LANGUAGE, TIME, MESSAGES
# -----------------------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.Account"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR /'staticfiles'
# STATICFILES_DIRS = [
#     'greatkart/static',
# ]

# MinIO Configuration (Production only)
USE_MINIO = config("USE_MINIO", default=False, cast=bool)

if USE_MINIO:
    MINIO_ENDPOINT = config("MINIO_ENDPOINT", default="localhost:9000")
    MINIO_ACCESS_KEY = config("MINIO_ACCESS_KEY", default="minioadmin")
    MINIO_SECRET_KEY = config("MINIO_SECRET_KEY", default="minioadmin")
    MINIO_BUCKET_NAME = config("MINIO_BUCKET_NAME", default="greatkart-media")
    MINIO_USE_HTTPS = config("MINIO_USE_HTTPS", default=False, cast=bool)

    # Configure MinIO storage backend
    STATIC_URL = f"{'https' if MINIO_USE_HTTPS else 'http'}://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/static/"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "greatkart.media_storages.MediaStorage"

else:
    # Local fallback for development
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "static"
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

STATICFILES_DIRS = [
    "greatkart/static",
]

# media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
