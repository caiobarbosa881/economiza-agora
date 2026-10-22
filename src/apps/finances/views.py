"""Views do perfil financeiro."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.finances.models import FinancialProfile
from apps.finances.serializers import FinancialProfileSerializer


class FinancialProfileView(generics.RetrieveUpdateAPIView):
    """Consulta e atualiza o perfil financeiro do usuário autenticado."""

    serializer_class = FinancialProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> FinancialProfile:
        """Retorna o perfil do usuário, criando-o zerado no primeiro acesso."""
        profile, _ = FinancialProfile.objects.get_or_create(user=self.request.user)
        return profile
