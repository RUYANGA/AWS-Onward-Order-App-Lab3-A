"""Root URL configuration.

The paths are part of the lab's contract with the infrastructure repository:
``/health`` is the ALB and ECS health check, and ``scripts/load-test.sh`` posts to
``/api/orders``.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.orders.urls")),
    path("api/", include("apps.orders.api.urls")),
]
