"""Test settings."""

from .base import *

STUDENT_NAME = "Test Student"
APP_VERSION = "test"
APP_ENV = "test"

# Tests render templates without running collectstatic first.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
WHITENOISE_USE_FINDERS = True
