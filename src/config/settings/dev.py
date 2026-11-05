"""Local development settings."""

from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Serve static files straight from each app's static/ folder; no collectstatic needed.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
