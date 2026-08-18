"""ProfilePresenter: a fonte dos campos que a API serializa."""

from datetime import date

import pytest

from apps.accounts.presenters import ProfilePresenter, UserPresenter
from apps.accounts.tests.factories import ProfileFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_reune_os_dados_que_moram_no_usuario() -> None:
    user = UserFactory.create(first_name="Ana", last_name="Souza", email="ana@example.com")

    presenter = ProfilePresenter(user.profile)

    assert presenter.name == "Ana Souza"
    assert presenter.first_name() == "Ana"
    assert presenter.last_name() == "Souza"
    assert presenter.email() == "ana@example.com"


def test_calcula_a_idade_a_partir_da_data_de_nascimento() -> None:
    profile = ProfileFactory.create(birth_date=date(1990, 1, 1))

    esperado = date.today().year - 1990 - ((date.today().month, date.today().day) < (1, 1))
    assert ProfilePresenter(profile).age == esperado


def test_idade_e_nula_sem_data_de_nascimento() -> None:
    profile = ProfileFactory.create(birth_date=None)

    assert ProfilePresenter(profile).age is None


def test_user_presenter_delega_ao_modelo() -> None:
    user = UserFactory.create(email="ana@example.com")

    assert UserPresenter(user).email == "ana@example.com"
