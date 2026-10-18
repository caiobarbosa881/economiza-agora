"""Testes de unidade do modelo ``User`` e do seu manager."""

import pytest

from apps.accounts.models import User

PASSWORD = "SenhaForte123"


@pytest.mark.django_db
def test_create_user_sem_email_levanta_value_error() -> None:
    """Criar usuário sem e-mail deve falhar com ``ValueError``."""
    with pytest.raises(ValueError, match="e-mail"):
        User.objects.create_user(email="", password=PASSWORD)


@pytest.mark.django_db
def test_create_user_normaliza_email_e_hasha_senha(db) -> None:
    """O e-mail é normalizado e a senha armazenada com hash."""
    user = User.objects.create_user(email="Novo@Example.COM", password=PASSWORD)

    assert user.email == "Novo@example.com"
    assert user.check_password(PASSWORD)
    assert user.password != PASSWORD
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser_padrao(db) -> None:
    """``create_superuser`` marca staff e superusuário por padrão."""
    admin = User.objects.create_superuser("admin@example.com", PASSWORD)

    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.check_password(PASSWORD)


@pytest.mark.django_db
def test_create_superuser_exige_is_staff(db) -> None:
    """``create_superuser`` recusa ``is_staff=False``."""
    with pytest.raises(ValueError, match="is_staff"):
        User.objects.create_superuser("a@example.com", PASSWORD, is_staff=False)


@pytest.mark.django_db
def test_create_superuser_exige_is_superuser(db) -> None:
    """``create_superuser`` recusa ``is_superuser=False``."""
    with pytest.raises(ValueError, match="is_superuser"):
        User.objects.create_superuser("a@example.com", PASSWORD, is_superuser=False)


@pytest.mark.django_db
def test_str_retorna_email(user: User) -> None:
    """A representação textual do usuário é o e-mail."""
    assert str(user) == user.email


@pytest.mark.django_db
def test_full_name_com_nome_e_sobrenome(user: User) -> None:
    """``full_name`` une nome e sobrenome."""
    user.last_name = "Silva"

    assert user.full_name == "Fulano Silva"


@pytest.mark.django_db
def test_full_name_sem_sobrenome(user: User) -> None:
    """``full_name`` não deixa espaço sobrando quando falta o sobrenome."""
    assert user.full_name == "Fulano"


@pytest.mark.django_db
def test_full_name_sem_nenhum_nome(db) -> None:
    """``full_name`` é vazio quando nome e sobrenome não foram preenchidos."""
    user = User.objects.create_user(email="vazio@example.com", password=PASSWORD)

    assert user.full_name == ""
