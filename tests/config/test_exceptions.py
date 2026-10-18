"""Testes do handler central de exceções da API."""

from apps.core.exceptions import BusinessRuleError
from config.exceptions import api_exception_handler


def test_erro_de_dominio_vira_400_com_detalhe_e_codigo() -> None:
    """Exceção de domínio é respondida como 400 com ``detail`` e ``code``."""
    response = api_exception_handler(BusinessRuleError("Regra violada."), {})

    assert response.status_code == 400
    assert response.data == {
        "detail": "Regra violada.",
        "code": "BusinessRuleError",
    }


def test_erro_padrao_do_drf_e_delegado() -> None:
    """Erros que não são de domínio seguem o handler padrão do DRF."""
    from rest_framework.exceptions import NotFound

    response = api_exception_handler(NotFound("Não encontrado."), {})

    assert response.status_code == 404
