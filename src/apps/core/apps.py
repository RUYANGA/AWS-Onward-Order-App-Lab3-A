"""Application configuration for the core app."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Cross-cutting features: health check, runtime info and the lab page context."""

    name = "apps.core"
    label = "core"
