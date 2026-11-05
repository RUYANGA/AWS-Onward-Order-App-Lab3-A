"""JSON API for quotes and orders, used by scripts and ``scripts/load-test.sh``."""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from ..exceptions import OrderError
from ..services import book, quote

#: Orders returned by ``GET /api/orders``.
LIST_LIMIT = 50


@require_GET
def quote_view(request):
    """Price a parcel without booking it.

    Query parameters: ``zone``, ``service`` and ``weight_kg``. Returns
    ``{"price": ..., "delivery_days": ...}`` or ``400`` with ``{"error": ...}``.
    """
    try:
        price, days = quote(
            request.GET.get("zone", ""),
            request.GET.get("service", ""),
            float(request.GET.get("weight_kg", "0")),
        )
    except (OrderError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"price": price, "delivery_days": days})


# No cookies, sessions or login are involved, so there is nothing for CSRF to protect.
@csrf_exempt
@require_http_methods(["GET", "POST"])
def orders_view(request):
    """List recent orders (``GET``) or book one from a JSON body (``POST``).

    ``POST`` returns ``201`` with the new order, or ``400`` with ``{"error": ...}``.
    """
    if request.method == "GET":
        return JsonResponse([o.to_dict() for o in book.recent(LIST_LIMIT)], safe=False)
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}
    try:
        order = book.create(
            data.get("merchant"),
            data.get("customer"),
            data.get("zone"),
            data.get("service"),
            data.get("weight_kg"),
        )
    except OrderError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse(order.to_dict(), status=201)
