"""Testes do filtro que mascara dados sensíveis nos logs."""

import logging

import pytest

from apps.core.log_filters import REDACTED, SensitiveDataFilter, redact

JWT = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.c2lnbmF0dXJh"


@pytest.mark.parametrize(
    ("mensagem", "segredo"),
    [
        ("payload={'email': 'a@b.com', 'password': 'SenhaForte123'}", "SenhaForte123"),
        ('{"refresh": "abc.def.ghi"}', "abc.def.ghi"),
        ("senha=minhaSenha&email=a@b.com", "minhaSenha"),
        ("new_password_confirm: Outra123", "Outra123"),
        ("Authorization: Bearer abc123.def-456", "abc123.def-456"),
        (f"token recebido {JWT}", JWT),
    ],
)
def test_redact_mascara_segredos(mensagem: str, segredo: str) -> None:
    """Senhas, tokens e cabeçalhos Bearer não aparecem na mensagem final."""
    resultado = redact(mensagem)

    assert segredo not in resultado
    assert REDACTED in resultado


def test_redact_preserva_mensagem_sem_segredos() -> None:
    """Mensagens comuns passam inalteradas."""
    mensagem = "Usuário a@b.com criou a categoria Alimentação"

    assert redact(mensagem) == mensagem


def test_filtro_sanitiza_mensagem_com_argumentos() -> None:
    """O filtro formata os args e mascara o resultado antes de emitir."""
    record = logging.LogRecord(
        name="teste",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="login com %s",
        args=({"email": "a@b.com", "password": "SenhaForte123"},),
        exc_info=None,
    )

    mantido = SensitiveDataFilter().filter(record)

    assert mantido is True
    assert record.args is None
    assert "SenhaForte123" not in record.getMessage()
    assert "a@b.com" in record.getMessage()
