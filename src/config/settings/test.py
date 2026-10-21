"""Configurações de teste (pytest).

Hermeticidade acima de tudo: a suíte não pode depender de Docker/Postgres
locais. Usa SQLite em memória para rodar em milissegundos e em qualquer
máquina. No CI, quem quiser validar contra Postgres real deve rodar com
``pytest --ds=config.settings.development`` e as variáveis ``POSTGRES_*``
definidas.
"""

from .development import *  # noqa: F401,F403

DEBUG = False

# Chave fixa e não secreta: a suíte não pode depender de ``.env`` (ex.: CI).
SECRET_KEY = "test-only-insecure-secret-key-not-for-production-use"
SIMPLE_JWT = {**SIMPLE_JWT, "SIGNING_KEY": SECRET_KEY}  # noqa: F405

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# E-mails capturados em memória (``mailoutbox`` do pytest-django).
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Throttling mantido com as rates base: o fixture autouse ``_reset_state``
# limpa o cache entre testes, então nenhum teste esbarra em limite de taxa.
# Testes de throttle específico sobrescrevem as rates via fixture ``settings``.

PASSWORD_HASHERS = [
    # Hasher rápido para acelerar a criação de usuários na suíte.
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
