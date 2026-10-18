"""Testes da permissão ``IsEmailVerified``."""

from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.accounts.permissions import IsEmailVerified


def _request_for(user) -> SimpleNamespace:
    """Monta um request mínimo com o usuário informado."""
    return SimpleNamespace(user=user)


def test_anonimo_e_negado() -> None:
    """Usuário anônimo não passa pela permissão."""
    permission = IsEmailVerified()

    assert permission.has_permission(_request_for(AnonymousUser()), None) is False


def test_autenticado_sem_verificacao_e_negado(user: User) -> None:
    """Usuário autenticado com e-mail não verificado é bloqueado."""
    permission = IsEmailVerified()

    assert permission.has_permission(_request_for(user), None) is False


def test_autenticado_verificado_e_permitido(verified_user: User) -> None:
    """Usuário autenticado com e-mail verificado tem acesso."""
    permission = IsEmailVerified()

    assert permission.has_permission(_request_for(verified_user), None) is True


def test_mensagem_de_erro_declarada() -> None:
    """A permissão expõe mensagem orientando a verificação do e-mail."""
    assert "verificar o e-mail" in IsEmailVerified.message
