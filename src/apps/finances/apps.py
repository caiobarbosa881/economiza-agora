"""Configuração do app ``finances``."""

from django.apps import AppConfig


class FinancesConfig(AppConfig):
    """Configuração do app de perfil financeiro."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.finances"
    label = "finances"
    verbose_name = "Finanças"
