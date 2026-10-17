"""Configuração do app ``core``."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuração do app base do projeto."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core"
