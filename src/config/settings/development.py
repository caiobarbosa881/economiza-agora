"""Configurações para o ambiente de desenvolvimento local."""

from .base import *  # noqa: F401,F403
from .base import env_bool

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Em desenvolvimento a API fica aberta para facilitar a exploração.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

if env_bool("DJANGO_DEBUG", default=True):
    INTERNAL_IPS = ["127.0.0.1"]
