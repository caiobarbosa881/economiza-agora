"""Serializers compartilhados entre os apps."""

from rest_framework import serializers


class DetailSerializer(serializers.Serializer):
    """Resposta padrão com uma mensagem legível em ``detail``.

    Usado para documentar (OpenAPI) endpoints que respondem apenas com uma
    mensagem de status.
    """

    detail = serializers.CharField()


class HealthCheckSerializer(serializers.Serializer):
    """Resposta do health check."""

    status = serializers.CharField()
    database = serializers.CharField()
