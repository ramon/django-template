from typing import ClassVar, cast

from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.utils.translation import gettext_lazy as _

from apps.core.domain import PersonName


class SignupForm(AllauthSignupForm):
    """
    Acrescenta um campo de nome completo ao cadastro do allauth.

    `DefaultAccountAdapter.save_user()` já lê `first_name`/`last_name` de
    `form.cleaned_data` sozinho -- não precisa de `ACCOUNT_ADAPTER` customizado,
    só preencher essas duas chaves aqui em `clean_name()`.
    """

    name = forms.CharField(label=_("Full name"), max_length=255)

    field_order: ClassVar[list[str]] = ["name", "email", "password1", "password2"]

    def clean_name(self) -> str:
        full_name = cast(str, self.cleaned_data["name"])
        try:
            person_name = PersonName.from_full_name(full_name)
        except ValueError as exc:
            raise forms.ValidationError(_("Enter your first and last name.")) from exc

        self.cleaned_data["first_name"] = person_name.first
        self.cleaned_data["last_name"] = person_name.last
        return full_name
