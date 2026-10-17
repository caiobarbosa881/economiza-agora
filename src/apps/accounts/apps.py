"""Configuração do app ``accounts``."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuração do app de contas e autenticação."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Contas"
