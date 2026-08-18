"""O unico endpoint da API. Nada o exercitava, entao ele estava em 0% de cobertura."""

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.test.utils import override_settings
from PIL import Image

from apps.accounts.models import User
from apps.accounts.services import gravatar_url

pytestmark = pytest.mark.django_db

URL = "/api/profile/me"


def _png() -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (1, 1), "white").save(buffer, format="PNG")
    return SimpleUploadedFile("avatar.png", buffer.getvalue(), content_type="image/png")


def test_exige_autenticacao(client: Client) -> None:
    """A NinjaAPI declara django_auth globalmente; o endpoint conta com isso."""
    assert client.get(URL).status_code == 401


def test_devolve_o_perfil_do_usuario_logado(auth_client: Client, user: User) -> None:
    response = auth_client.get(URL)

    assert response.status_code == 200
    assert response.json() == {
        "sub": str(user.profile.id),
        "name": f"{user.first_name} {user.last_name}",
        "given_name": user.first_name,
        "family_name": user.last_name,
        "picture": gravatar_url(user.email),
        "email": user.email,
    }


def test_picture_cai_no_gravatar_quando_nao_ha_avatar(auth_client: Client, user: User) -> None:
    """Sem este caminho o AvatarMixin.avatar_url e o gravatar_url seriam codigo morto."""
    assert auth_client.get(URL).json()["picture"] == gravatar_url(user.email)


def test_picture_aponta_para_o_arquivo_enviado(
    auth_client: Client, user: User, tmp_path: object
) -> None:
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        user.profile.avatar = _png()
        user.profile.save()

        picture = auth_client.get(URL).json()["picture"]

    assert picture is not None
    assert picture.endswith(".png")


def test_o_payload_expoe_so_os_campos_do_schema(auth_client: Client) -> None:
    """Um campo a mais aqui e' vazamento de dado; um a menos quebra o cliente."""
    assert set(auth_client.get(URL).json()) == {
        "sub",
        "name",
        "given_name",
        "family_name",
        "picture",
        "email",
    }


def test_o_schema_openapi_descreve_o_endpoint(client: Client) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert "/api/profile/me" in response.json()["paths"]
