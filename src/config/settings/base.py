"""Settings shared by every environment.

The container runs on ECS Fargate with a read-only root filesystem (only /tmp is
writable) and keeps orders in memory, so there is no database, no sessions and no
login. Everything that changes between environments comes from environment
variables (or a local ``.env`` file, see ``.env.example``).
"""

from pathlib import Path

import environ
from django.core.management.utils import get_random_secret_key

# BASE_DIR -> src/, ROOT_DIR -> repository root (holds .env, Docker files, requirements)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

env = environ.Env(
    DEBUG=(bool, False),
    # The ALB forwards requests with its own DNS name as Host, which is only known
    # after the stack is created. Tasks are reachable only through the ALB
    # (app-sg in the infra repo), so any host is accepted unless this is set.
    ALLOWED_HOSTS=(list, ["*"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
)
environ.Env.read_env(ROOT_DIR / ".env")

# Nothing is signed with the key (no sessions, no login), so a per-process fallback
# is safe. Set SECRET_KEY if sessions or authentication are ever added.
SECRET_KEY = env("SECRET_KEY", default=None) or get_random_secret_key()
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# ------------------------------------------------------------------- Lab
# Shown on every page. Set STUDENT_NAME before your first push (here or as an env var).
STUDENT_NAME = env("STUDENT_NAME", default="Merci RUYANGA")
LAB_NAME = "Delivering Order System Updates Safely for Onward Logistics"
APP_VERSION = env("APP_VERSION", default="local")  # short git SHA, baked in at build time
APP_ENV = env("APP_ENV", default="local")  # set by the ECS task definition

# ------------------------------------------------------------------- Apps
DJANGO_APPS = [
    "django.contrib.staticfiles",
]
LOCAL_APPS = [
    "apps.core",
    "apps.orders",
]
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    # Must stay first: answers ALB/ECS health checks before host validation.
    "apps.core.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "apps.core.context_processors.lab",
            ],
        },
    },
]

# Orders are kept in memory per container (see apps/orders/services/order_book.py),
# so no database is configured and there are no migrations.
DATABASES = {}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# Static files are collected into the image at build time and served by WhiteNoise,
# so nothing is written to disk at runtime.
STATIC_URL = "static/"
STATIC_ROOT = ROOT_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
# Only the hashed copies are ever served; dropping originals shrinks the image.
WHITENOISE_KEEP_ONLY_HASHED_FILES = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{asctime} [{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"handlers": ["console"], "level": env("LOG_LEVEL", default="INFO")},
}
