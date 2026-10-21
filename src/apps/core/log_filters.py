"""Filtros de logging da aplicação."""

import logging
import re

REDACTED = "[REDACTED]"

# Ordem importa: chaves sensíveis primeiro, depois tokens soltos.
_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # "password": "x", 'token': 'x', senha=x, refresh=x ...
    (
        re.compile(
            r"""(?ix)
            (["']?\b\w*(?:password|senha|token|refresh|access|secret)\w*["']?\s*[:=]\s*)
            ("[^"]*"|'[^']*'|[^\s,}&]+)
            """
        ),
        rf"\1'{REDACTED}'",
    ),
    (re.compile(r"(?i)\bBearer\s+[\w\-.~+/]+=*"), f"Bearer {REDACTED}"),
    # JWT solto (header.payload.signature em base64url).
    (re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]+"), REDACTED),
]


def redact(text: str) -> str:
    """Substitui senhas, tokens e segredos encontrados no texto.

    Args:
        text: Mensagem de log já formatada.

    Returns:
        A mensagem com os valores sensíveis mascarados.
    """
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class SensitiveDataFilter(logging.Filter):
    """Mascara dados sensíveis (senhas, tokens JWT) antes de emitir o log."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Reescreve a mensagem do registro já sem dados sensíveis.

        Args:
            record: Registro de log a ser emitido.

        Returns:
            Sempre ``True``: o registro é mantido, apenas sanitizado.
        """
        record.msg = redact(record.getMessage())
        record.args = None
        return True
