"""Testes da postura de segurança das settings de produção."""


def test_production_aplica_postura_segura() -> None:
    """As settings de produção desligam DEBUG e ligam proteções de HTTPS."""
    from config.settings import production

    assert production.DEBUG is False
    assert production.SECURE_SSL_REDIRECT is True
    assert production.SESSION_COOKIE_SECURE is True
    assert production.CSRF_COOKIE_SECURE is True
    assert production.SECURE_CONTENT_TYPE_NOSNIFF is True
    assert production.SECURE_HSTS_SECONDS == 31536000
    assert production.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert production.SECURE_HSTS_PRELOAD is True


def test_production_restringe_renderers() -> None:
    """Produção serve apenas JSON (sem Browsable API)."""
    from config.settings import production

    renderers = production.REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
    assert renderers == ["rest_framework.renderers.JSONRenderer"]
