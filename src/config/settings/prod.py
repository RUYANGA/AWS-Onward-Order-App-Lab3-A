"""Production settings (ECS Fargate behind the Application Load Balancer)."""

from .base import *
from .base import env

DEBUG = False

# The lab's ALB listens on plain HTTP (port 80 and the 8080 test listener), so
# HTTPS-only settings are off by default. Set USE_HTTPS=true once an HTTPS
# listener with a certificate is in front of the service.
USE_HTTPS = env.bool("USE_HTTPS", default=False)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = USE_HTTPS
CSRF_COOKIE_SECURE = USE_HTTPS
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000) if USE_HTTPS else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = USE_HTTPS
SECURE_HSTS_PRELOAD = USE_HTTPS

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
