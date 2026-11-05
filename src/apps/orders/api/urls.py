"""URL routes for the orders API, mounted at ``/api/``."""

from django.urls import path

from . import views

app_name = "orders-api"

urlpatterns = [
    path("quote", views.quote_view, name="quote"),
    path("orders", views.orders_view, name="orders"),
]
