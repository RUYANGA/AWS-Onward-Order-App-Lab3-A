"""Views for the core app."""

from django.http import JsonResponse
from django.views.decorators.http import require_safe

from .health import health_report


@require_safe
def health(request):
    """Liveness probe for the ALB target groups and the ECS container health check.

    Requests are normally answered by ``HealthCheckMiddleware``; this view serves
    the endpoint if the middleware is ever removed.
    """
    payload, status = health_report()
    return JsonResponse(payload, status=status)
