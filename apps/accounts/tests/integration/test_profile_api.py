"""The API's only endpoint. Nothing exercised it, so it sat at 0% coverage."""

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


def test_requires_authentication(client: Client) -> None:
    """NinjaAPI declares django_auth globally; the endpoint relies on that."""
    assert client.get(URL).status_code == 401


def test_returns_the_logged_in_user_profile(auth_client: Client, user: User) -> None:
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


def test_picture_falls_back_to_gravatar_without_an_avatar(auth_client: Client, user: User) -> None:
    """Without this path, AvatarMixin.avatar_url and gravatar_url would be dead code."""
    assert auth_client.get(URL).json()["picture"] == gravatar_url(user.email)


def test_picture_points_to_the_uploaded_file(
    auth_client: Client, user: User, tmp_path: object
) -> None:
    with override_settings(MEDIA_ROOT=str(tmp_path)):
        user.profile.avatar = _png()
        user.profile.save()

        picture = auth_client.get(URL).json()["picture"]

    assert picture is not None
    assert picture.endswith(".png")


def test_payload_exposes_only_the_schema_fields(auth_client: Client) -> None:
    """An extra field here is a data leak; a missing one breaks the client."""
    assert set(auth_client.get(URL).json()) == {
        "sub",
        "name",
        "given_name",
        "family_name",
        "picture",
        "email",
    }


def test_openapi_schema_describes_the_endpoint(client: Client) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert "/api/profile/me" in response.json()["paths"]
