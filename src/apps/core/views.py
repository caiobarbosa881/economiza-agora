"""Views do app ``core``."""

import logging

from django.db import DatabaseError, connection
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers import HealthCheckSerializer

logger = logging.getLogger(__name__)


def database_is_available() -> bool:
    """Confere se o banco de dados responde a uma consulta simples.

    Returns:
        ``True`` se a consulta for executada com sucesso.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        logger.exception("Health check: banco de dados indisponível.")
        return False
    return True


@extend_schema(responses={200: HealthCheckSerializer, 503: HealthCheckSerializer})
@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])  # monitores e load balancers consultam com frequência
def health_check(request: Request) -> Response:
    """Verifica se a aplicação e o banco de dados estão no ar.

    Args:
        request: Requisição HTTP recebida.

    Returns:
        200 com ``status: ok`` ou 503 se o banco estiver indisponível.
    """
    if not database_is_available():
        return Response(
            {"status": "error", "database": "unavailable"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response({"status": "ok", "database": "ok"}, status=status.HTTP_200_OK)
