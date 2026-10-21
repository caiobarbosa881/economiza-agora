"""Testes da postura de segurança das settings de produção."""

import importlib
import sys
from types import ModuleType

import pytest


@pytest.fixture
def production(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """Importa as settings de produção com uma SECRET_KEY definida.

    Não depende do ``.env``: injeta a chave em ``base`` e força uma importação
    nova de ``production`` (o monkeypatch restaura tudo ao final).
    """
    from config.settings import base

    monkeypatch.delenv("DJANGO_BEHIND_PROXY", raising=False)
    monkeypatch.setattr(base, "SECRET_KEY", "prod-test-secret-key")
    monkeypatch.delitem(sys.modules, "config.settings.production", raising=False)
    return importlib.import_module("config.settings.production")


def test_production_aplica_postura_segura(production: ModuleType) -> None:
    """As settings de produção desligam DEBUG e ligam proteções de HTTPS."""
    assert production.DEBUG is False
    assert production.SECURE_SSL_REDIRECT is True
    assert production.SESSION_COOKIE_SECURE is True
    assert production.CSRF_COOKIE_SECURE is True
    assert production.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert production.SECURE_HSTS_SECONDS == 31536000
    assert production.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert production.SECURE_HSTS_PRELOAD is True


def test_production_restringe_renderers(production: ModuleType) -> None:
    """Produção serve apenas JSON (sem Browsable API)."""
    renderers = production.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
    assert renderers == ["rest_framework.renderers.JSONRenderer"]


def test_production_restringe_documentacao_a_equipe(production: ModuleType) -> None:
    """Em produção o schema/Swagger só é servido para usuários staff."""
    permissions = production.SPECTACULAR_SETTINGS["SERVE_PERMISSIONS"]
    assert permissions == ["rest_framework.permissions.IsAdminUser"]


def test_production_exige_secret_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem DJANGO_SECRET_KEY, importar as settings de produção falha."""
    from config.settings import base

    monkeypatch.setattr(base, "SECRET_KEY", "")
    monkeypatch.delitem(sys.modules, "config.settings.production", raising=False)

    with pytest.raises(RuntimeError, match="DJANGO_SECRET_KEY"):
        importlib.import_module("config.settings.production")


def test_production_sem_proxy_nao_confia_em_x_forwarded_proto(production: ModuleType) -> None:
    """Por padrão o cabeçalho de proxy não é aceito (evita HTTPS forjado)."""
    assert not hasattr(production, "SECURE_PROXY_SSL_HEADER")


def test_production_atras_de_proxy_confia_em_x_forwarded_proto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Com DJANGO_BEHIND_PROXY, o Django reconhece HTTPS vindo do proxy."""
    from config.settings import base

    monkeypatch.setenv("DJANGO_BEHIND_PROXY", "True")
    monkeypatch.setattr(base, "SECRET_KEY", "prod-test-secret-key")
    monkeypatch.delitem(sys.modules, "config.settings.production", raising=False)

    production = importlib.import_module("config.settings.production")

    assert production.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
