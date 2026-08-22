"""
SignupForm: quebra o campo "name" em first_name/last_name pro adapter do allauth.

`clean_name()` é testado chamando-o direto, sem passar por `is_valid()` -- o
`clean_email()` herdado do allauth bate no banco (checa e-mail duplicado), e essa
consulta não é responsabilidade deste form. O fluxo completo (banco incluído) é
coberto por teste de integração, em cima da view real de cadastro.
"""

import pytest
from django import forms

from apps.accounts.forms import SignupForm


def _form_with_name(name: str) -> SignupForm:
    form = SignupForm()
    form.cleaned_data = {"name": name}
    return form


def test_splits_a_full_name_into_first_and_last_name() -> None:
    form = _form_with_name("ana souza")

    form.clean_name()

    assert form.cleaned_data["first_name"] == "Ana"
    assert form.cleaned_data["last_name"] == "Souza"


def test_keeps_a_middle_name_as_part_of_the_last_name() -> None:
    form = _form_with_name("ana paula souza")

    form.clean_name()

    assert form.cleaned_data["first_name"] == "Ana"
    assert form.cleaned_data["last_name"] == "Paula Souza"


def test_rejects_a_name_without_a_space() -> None:
    form = _form_with_name("ana")

    with pytest.raises(forms.ValidationError):
        form.clean_name()
