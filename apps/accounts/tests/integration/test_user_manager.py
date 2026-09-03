"""UserManager.create_user/create_superuser hit the database (Profile.objects.create,
User.save), unlike the pure factories used by every other test's `user` fixture."""

import pytest

from apps.accounts.models import User

pytestmark = pytest.mark.django_db


def test_create_user_requires_an_email() -> None:
    with pytest.raises(ValueError, match="The Email must be set"):
        User.objects.create_user(email="", password="senha-de-teste-123")


def test_create_user_creates_an_associated_profile() -> None:
    user = User.objects.create_user(
        email="ada@example.com",
        password="senha-de-teste-123",
        first_name="Ada",
        last_name="Lovelace",
        phone_number="+5511987654321",
    )

    assert user.profile is not None


def test_create_superuser_sets_staff_and_superuser_flags() -> None:
    user = User.objects.create_superuser(
        email="root@example.com",
        password="senha-de-teste-123",
        first_name="Root",
        last_name="User",
        phone_number="+5511987654322",
    )

    assert user.is_staff is True
    assert user.is_superuser is True
