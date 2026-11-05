"""URL routes for the order page."""

from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.home, name="home"),
    path("orders", views.place_order, name="place_order"),
]
