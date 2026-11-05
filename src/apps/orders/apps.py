"""Application configuration for the orders app."""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Booking deliveries: pricing, delivery estimates, the order page and the JSON API."""

    name = "apps.orders"
    label = "orders"
