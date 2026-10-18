"""Testes de unidade/integração dos serializers de ``accounts``."""

from unittest.mock import MagicMock

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    EmailVerificationSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    RegisterSerializer,
)

PASSWORD = "SenhaForte123"


def _context(user: User) -> dict:
    """Monta o contexto ``request`` exigido pelos serializers de conta."""
    request = MagicMock()
    request.user = user
    return {"request": request}


@pytest.mark.django_db
def test_register_validate_email_rejeita_duplicado(user: User) -> None:
    """E-mail já cadastrado é rejeitado com mensagem explícita."""
    serializer = RegisterSerializer()

    with pytest.raises(ValidationError) as exc_info:
        serializer.validate_email(user.email)

    assert "Já existe um usuário com este e-mail." in str(exc_info.value)


@pytest.mark.django_db
def test_register_validate_normaliza_email_para_minusculo(db) -> None:
    """E-mail aceito é devolvido em minúsculas."""
    serializer = RegisterSerializer()

    assert serializer.validate_email("Novo@Example.COM") == "novo@example.com"


@pytest.mark.django_db
def test_register_is_valid_aponta_confirmação_divergente(db) -> None:
    """Confirmação de senha divergente falha no campo ``password_confirm``."""
    serializer = RegisterSerializer(
        data={
            "email": "novo@example.com",
            "password": PASSWORD,
            "password_confirm": "OutraSenha123",
        }
    )

    assert serializer.is_valid() is False
    assert "password_confirm" in serializer.errors


@pytest.mark.django_db
def test_password_change_rejeita_confirmacao_divergente(user: User) -> None:
    """Nova senha e confirmação diferentes falham na validação."""
    serializer = PasswordChangeSerializer(
        data={
            "current_password": PASSWORD,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "OutraSenha123",
        },
        context=_context(user),
    )

    assert serializer.is_valid() is False
    assert "new_password_confirm" in serializer.errors


@pytest.mark.django_db
def test_password_reset_confirm_rejeita_confirmacao_divergente(user: User) -> None:
    """Confirmação divergente na redefinição falha no campo esperado."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    serializer = PasswordResetConfirmSerializer(
        data={
            "uid": uid,
            "token": token,
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "OutraSenha123",
        }
    )

    assert serializer.is_valid() is False
    assert "new_password_confirm" in serializer.errors


@pytest.mark.django_db
def test_password_reset_confirm_rejeita_uid_invalido(db) -> None:
    """UID que não decodifica para um usuário é rejeitado no campo ``uid``."""
    serializer = PasswordResetConfirmSerializer(
        data={
            "uid": "nao-e-um-uid",
            "token": "qualquer",
            "new_password": "NovaSenhaForte123",
            "new_password_confirm": "NovaSenhaForte123",
        }
    )

    assert serializer.is_valid() is False
    assert "uid" in serializer.errors


@pytest.mark.django_db
def test_email_verification_rejeita_uid_invalido(db) -> None:
    """UID inválido também é rejeitado na verificação de e-mail."""
    serializer = EmailVerificationSerializer(
        data={"uid": "nao-e-um-uid", "token": "qualquer"}
    )

    assert serializer.is_valid() is False
    assert "uid" in serializer.errors


@pytest.mark.django_db
def test_email_verification_rejeita_ja_verificado(verified_user: User) -> None:
    """E-mail já verificado é rejeitado antes da checagem do token."""
    uid = urlsafe_base64_encode(force_bytes(verified_user.pk))
    serializer = EmailVerificationSerializer(
        data={"uid": uid, "token": "qualquer"}
    )

    assert serializer.is_valid() is False
    assert "detail" in serializer.errors


@pytest.mark.django_db
def test_token_de_login_inclui_claim_de_email(user: User) -> None:
    """O token JWT de login carrega o e-mail como claim."""
    token = CustomTokenObtainPairSerializer.get_token(user)

    assert token["email"] == user.email
