"""The catalogs: where they live and the form they're written in."""

from pathlib import Path

import pytest
from django.conf import settings
from django.utils import translation
from django.utils.translation import pgettext

from apps.core.management.commands.makemessages import Command as MakeMessages

CATALOGS = sorted(MakeMessages.project_catalogs())
ROOT = Path(settings.BASE_DIR) / "locale" / "pt_BR" / "LC_MESSAGES" / "django.po"
ACCOUNTS = Path(settings.BASE_DIR) / "apps/accounts/locale/pt_BR/LC_MESSAGES/django.po"


def test_a_catalog_exists_for_every_declared_language() -> None:
    locales = {c.parts[-3] for c in CATALOGS}

    assert locales == {translation.to_locale(code) for code, _ in settings.LANGUAGES}


def test_app_strings_stay_in_the_app_catalog() -> None:
    """`pgettext("model", ...)` lives in apps/accounts; the root catalog cannot receive it."""
    assert 'msgctxt "model"' in ACCOUNTS.read_text(encoding="utf-8")
    assert 'msgctxt "model"' not in ROOT.read_text(encoding="utf-8")


def test_the_root_catalog_only_holds_what_is_not_from_an_app() -> None:
    """What's left is what lives in config/ and templates/ -- here, the language names."""
    content = ROOT.read_text(encoding="utf-8")

    assert 'msgid "Brazilian Portuguese"' in content
    assert 'msgid "File size must be less than %sMB"' not in content


@pytest.mark.parametrize("catalog", CATALOGS, ids=lambda c: str(c.relative_to(settings.BASE_DIR)))
def test_catalog_is_written_without_noise(catalog: Path) -> None:
    """No `#:` (location), no `#~` (obsolete), and no generation date."""
    lines = catalog.read_text(encoding="utf-8").splitlines()

    assert not [line for line in lines if line.startswith("#:")]
    assert not [line for line in lines if line.startswith("#~")]
    assert not [line for line in lines if line.startswith('"POT-Creation-Date:')]


def test_the_command_defaults_to_no_location_and_no_obsolete() -> None:
    """This is what keeps the .po files readable -- it cannot depend on remembering the flag."""
    command = MakeMessages()
    options = command.create_parser("manage.py", "makemessages").parse_args([])

    assert options.no_location is True
    assert options.no_obsolete is True


def test_app_translation_resolves_at_runtime() -> None:
    if not ACCOUNTS.with_suffix(".mo").exists():
        pytest.skip("catálogo não compilado; rode `manage.py compilemessages`")

    with translation.override("pt-br"):
        assert pgettext("model", "user") == "usuário"

    with translation.override("en"):
        assert pgettext("model", "user") == "user"
