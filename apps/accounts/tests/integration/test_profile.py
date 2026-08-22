"""Profile.save() runs full_clean() (BaseModel), so the document/nationality
coupling can't be bypassed by a direct save -- exercised end to end against the
database, unlike the pure-clean() unit tests in tests/unit/models/."""

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.accounts.tests.factories import ProfileFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_save_rejects_a_nationality_without_a_document(user: User) -> None:
    user.profile.nationality = "BR"

    with pytest.raises(ValidationError):
        user.profile.save()


def test_save_normalizes_and_persists_a_valid_document(user: User) -> None:
    user.profile.nationality = "BR"
    user.profile.document = "529.982.247-25"
    user.profile.save()

    user.profile.refresh_from_db()
    assert user.profile.document == "52998224725"
    assert user.profile.document_type == "cpf"


def test_save_rejects_a_duplicate_document() -> None:
    ProfileFactory.create(nationality="BR", document="529.982.247-25")
    other_user = UserFactory.create()

    other_user.profile.nationality = "BR"
    other_user.profile.document = "52998224725"

    with pytest.raises(ValidationError):
        other_user.profile.save()
