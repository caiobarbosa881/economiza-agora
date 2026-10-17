"""Configurações para o ambiente de desenvolvimento local."""

from .base import *  # noqa: F401,F403
from .base import env_bool

DEBUG = True

ALLOWED_HOSTS = ["*"]

# E-mails são exibidos no console durante o desenvolvimento.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

if env_bool("DJANGO_DEBUG", default=True):
    INTERNAL_IPS = ["127.0.0.1"]
