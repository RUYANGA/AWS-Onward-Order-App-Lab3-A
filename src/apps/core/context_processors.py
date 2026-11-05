"""Template context shared by every page."""

from django.conf import settings

from .runtime import task_info


def lab(request):
    """Add who built the app, which release is live and which task answered.

    Args:
        request: The current HTTP request (unused, required by Django).

    Returns:
        Template variables ``student_name``, ``lab_name``, ``version``, ``env`` and
        ``runtime``.
    """
    return {
        "student_name": settings.STUDENT_NAME,
        "lab_name": settings.LAB_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
        "runtime": task_info(),
    }
