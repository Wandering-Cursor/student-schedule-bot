from .base import *  # noqa: F403
from .base import LOGGING, config

SECURE_SSL_REDIRECT = True
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

LOGGING["handlers"]["console"]["level"] = "WARNING"
CSRF_TRUSTED_ORIGINS = config.TRUSTED_HOSTS
CORS_ALLOW_ALL_ORIGINS = True

STATIC_URL = "/schedule/static/"
MEDIA_URL = "/schedule/media/"

STATIC_ROOT = "/app/static/"
MEDIA_ROOT = "/app/media/"
