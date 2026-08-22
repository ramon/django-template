"""
Cadastro via /auth/signup/, fim a fim: exercita o SignupForm, o
DefaultAccountAdapter.save_user() do allauth e o full_clean() automático do
BaseModel.save() (ADR 0011) juntos -- é essa combinação que quebrava com HTTP 500
antes do SignupForm ganhar o campo "name" (apps/accounts/forms.py).
"""

import pytest
from django.test import Client

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_signup_creates_a_user_with_first_and_last_name(client: Client) -> None:
    response = client.post(
        "/auth/signup/",
        data={
            "name": "ana paula souza",
            "email": "ana@example.com",
            "password1": "senha-forte-123",
            "password2": "senha-forte-123",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/confirm-email/"
    user = User.objects.get(email="ana@example.com")
    assert user.first_name == "Ana"
    assert user.last_name == "Paula Souza"


def test_signup_rejects_a_name_without_a_space(client: Client) -> None:
    response = client.post(
        "/auth/signup/",
        data={
            "name": "ana",
            "email": "ana@example.com",
            "password1": "senha-forte-123",
            "password2": "senha-forte-123",
        },
    )

    assert response.status_code == 200
    assert not User.objects.filter(email="ana@example.com").exists()


def test_signup_page_shows_the_translated_label(client: Client) -> None:
    response = client.get("/auth/signup/")
    assert "Nome completo" in response.content.decode()
