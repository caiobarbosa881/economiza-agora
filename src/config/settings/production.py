"""Configurações para o ambiente de produção.

Exige que ``DJANGO_SECRET_KEY`` esteja definida e aplica posturas
restritivas de segurança.
"""

from .base import *  # noqa: F401,F403
from .base import SECRET_KEY, env_bool, env_list

DEBUG = False

if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY deve ser definida em produção.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=[])

REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# Em produção o schema e a documentação da API ficam restritos à equipe.
SPECTACULAR_SETTINGS = {
    **SPECTACULAR_SETTINGS,  # noqa: F405
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
}

# Atrás de um proxy/load balancer que termina o TLS, o Django só sabe que a
# requisição original era HTTPS por este cabeçalho. Ative apenas se o proxy
# sempre sobrescrever o X-Forwarded-Proto; caso contrário o cliente poderia
# forjá-lo.
if env_bool("DJANGO_BEHIND_PROXY", default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
