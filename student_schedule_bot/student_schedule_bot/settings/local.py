from .base import *  # noqa: F403
from .base import LOGGING

LOGGING["handlers"]["console"]["level"] = "INFO"

CORS_ALLOW_ALL_ORIGINS = True
