"""ProfilePresenter: the source of the fields the API serializes."""

from datetime import date

import pytest

from apps.accounts.presenters import ProfilePresenter, UserPresenter
from apps.accounts.tests.factories import ProfileFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_gathers_the_data_that_lives_on_the_user() -> None:
    user = UserFactory.create(first_name="Ana", last_name="Souza", email="ana@example.com")

    presenter = ProfilePresenter(user.profile)

    assert presenter.name == "Ana Souza"
    assert presenter.first_name() == "Ana"
    assert presenter.last_name() == "Souza"
    assert presenter.email() == "ana@example.com"


def test_calculates_age_from_birth_date() -> None:
    profile = ProfileFactory.create(birth_date=date(1990, 1, 1))

    expected = date.today().year - 1990 - ((date.today().month, date.today().day) < (1, 1))
    assert ProfilePresenter(profile).age == expected


def test_age_is_none_without_a_birth_date() -> None:
    profile = ProfileFactory.create(birth_date=None)

    assert ProfilePresenter(profile).age is None


def test_user_presenter_delegates_to_the_model() -> None:
    user = UserFactory.create(email="ana@example.com")

    assert UserPresenter(user).email == "ana@example.com"
