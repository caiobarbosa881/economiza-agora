"""Modelo de usuário customizado com login por e-mail."""

from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager["User"]):
    """Gerencia a criação de usuários usando o e-mail como identificador."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: Any) -> "User":
        """Cria e persiste um usuário com o e-mail normalizado.

        Args:
            email: Endereço de e-mail do usuário.
            password: Senha em texto puro (será armazenada com hash).
            **extra_fields: Campos adicionais do modelo.

        Returns:
            A instância de usuário criada.

        Raises:
            ValueError: Se o e-mail não for informado.
        """
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        """Cria um usuário comum.

        Args:
            email: Endereço de e-mail do usuário.
            password: Senha em texto puro.
            **extra_fields: Campos adicionais do modelo.

        Returns:
            A instância de usuário criada.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> "User":
        """Cria um superusuário.

        Args:
            email: Endereço de e-mail do superusuário.
            password: Senha em texto puro.
            **extra_fields: Campos adicionais do modelo.

        Returns:
            A instância de superusuário criada.

        Raises:
            ValueError: Se ``is_staff`` ou ``is_superuser`` não forem verdadeiros.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("O superusuário precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("O superusuário precisa ter is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Usuário da aplicação autenticado por e-mail."""

    email = models.EmailField("e-mail", unique=True)
    first_name = models.CharField("nome", max_length=150, blank=True)
    last_name = models.CharField("sobrenome", max_length=150, blank=True)
    is_active = models.BooleanField("ativo", default=True)
    is_staff = models.BooleanField("equipe", default=False)
    is_email_verified = models.BooleanField("e-mail verificado", default=False)
    date_joined = models.DateTimeField("data de cadastro", default=timezone.now)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        """Retorna o e-mail como representação textual."""
        return self.email

    @property
    def full_name(self) -> str:
        """Retorna o nome completo do usuário."""
        return f"{self.first_name} {self.last_name}".strip()
