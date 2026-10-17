"""Handler de exceções da API.

Padroniza as respostas de erro e garante que erros de domínio não vazem
detalhes internos (stack traces) para o cliente.
"""

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from apps.core.exceptions import EconomizaAgoraError


def api_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Trata exceções de domínio e delega o restante ao DRF.

    Args:
        exc: Exceção capturada durante a requisição.
        context: Contexto da view que gerou a exceção.

    Returns:
        Uma ``Response`` padronizada ou o resultado do handler padrão do DRF.
    """
    if isinstance(exc, EconomizaAgoraError):
        return Response(
            {"detail": str(exc), "code": exc.__class__.__name__},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return exception_handler(exc, context)
