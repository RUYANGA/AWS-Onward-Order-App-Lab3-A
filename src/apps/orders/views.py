"""Web UI: the booking page and its form."""

from datetime import date
from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .constants import SERVICES, ZONES
from .exceptions import OrderError
from .services import book


def _rows(orders):
    """Pair each order with the labels and arrival date the table shows."""
    return [
        {
            "order": o,
            "service_label": SERVICES[o.service]["label"],
            "zone_label": ZONES[o.zone]["label"],
            "eta": date.fromisoformat(o.estimated_delivery),
        }
        for o in orders
    ]


def _page(request, *, error=None, form=None, status=200):
    context = {
        "rows": _rows(book.recent()),
        "zones": ZONES,
        "services": SERVICES,
        "error": error,
        "form": form or {},
    }
    return render(request, "orders/index.html", context, status=status)


@require_GET
def home(request):
    """Show the booking form and the orders booked on this task."""
    return _page(request)


@require_POST
def place_order(request):
    """Book a delivery from the form, then redirect back to the page.

    On invalid input the page is shown again with the error and the values entered.
    """
    form = request.POST
    try:
        order = book.create(
            form.get("merchant"),
            form.get("customer"),
            form.get("zone"),
            form.get("service"),
            form.get("weight_kg"),
        )
    except OrderError as exc:
        return _page(request, error=str(exc), form=form, status=400)
    return HttpResponseRedirect(f"{reverse('orders:home')}?{urlencode({'placed': order.id})}")
