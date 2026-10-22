"""Rotas do app ``finances``."""

from django.urls import path

from apps.finances.views import FinancialProfileView

app_name = "finances"

urlpatterns = [
    path("profile/", FinancialProfileView.as_view(), name="profile"),
]
