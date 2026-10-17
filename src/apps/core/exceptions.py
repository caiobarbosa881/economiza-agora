"""Exceções customizadas da aplicação.

Toda exceção de domínio deve herdar de :class:`EconomizaAgoraError` para
permitir tratamento centralizado.
"""


class EconomizaAgoraError(Exception):
    """Exceção base para todos os erros de domínio do projeto."""


class ResourceNotFoundError(EconomizaAgoraError):
    """Sinaliza que um recurso solicitado não foi encontrado."""


class BusinessRuleError(EconomizaAgoraError):
    """Sinaliza violação de uma regra de negócio."""
