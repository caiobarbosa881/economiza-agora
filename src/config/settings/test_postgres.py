"""Configurações de teste contra PostgreSQL real.

Igual a ``config.settings.test``, mas usa o banco definido pelas variáveis
``POSTGRES_*``. Pega diferenças que o SQLite deixa passar (tipos, constraints,
ordenação). Usado no CI: ``pytest --ds=config.settings.test_postgres``.
"""

import os

from .base import build_databases
from .test import *  # noqa: F401,F403

if not os.environ.get("POSTGRES_DB"):
    raise RuntimeError("config.settings.test_postgres exige POSTGRES_DB definido.")

DATABASES = build_databases()
