"""Service health check used by the ALB target groups and the ECS container check."""

from django.conf import settings

from .runtime import task_info

#: URL path of the health endpoint, shared by the middleware, the URL config and
#: the infrastructure (``HealthCheckPath`` in the infra repo's service.yaml).
HEALTH_PATH = "/health"


def health_report():
    """Report that the process is up and which release and task is answering.

    The app has no database or other dependency to check: if this code runs, the
    container can serve orders.

    Returns:
        A ``(payload, status_code)`` tuple, e.g.
        ``({"status": "ok", "version": "abc1234", "task": "...", "zone": "..."}, 200)``.
    """
    return {"status": "ok", "version": settings.APP_VERSION, **task_info()}, 200
