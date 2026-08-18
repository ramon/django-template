"""Os catálogos: onde ficam e em que forma são escritos."""

from pathlib import Path

import pytest
from django.conf import settings
from django.utils import translation
from django.utils.translation import pgettext

from apps.core.management.commands.makemessages import Command as MakeMessages

CATALOGOS = sorted(MakeMessages.catalogos_do_projeto())
RAIZ = Path(settings.BASE_DIR) / "locale" / "pt_BR" / "LC_MESSAGES" / "django.po"
ACCOUNTS = Path(settings.BASE_DIR) / "apps/accounts/locale/pt_BR/LC_MESSAGES/django.po"


def test_existe_catalogo_para_cada_idioma_declarado() -> None:
    locales = {c.parts[-3] for c in CATALOGOS}

    assert locales == {translation.to_locale(code) for code, _ in settings.LANGUAGES}


def test_as_strings_do_app_ficam_no_catalogo_do_app() -> None:
    """`pgettext("model", ...)` vive em apps/accounts; a raiz não pode recebê-lo."""
    assert 'msgctxt "model"' in ACCOUNTS.read_text(encoding="utf-8")
    assert 'msgctxt "model"' not in RAIZ.read_text(encoding="utf-8")


def test_a_raiz_guarda_so_o_que_nao_e_de_app() -> None:
    """Sobra o que vive em config/ e templates/ -- aqui, os nomes dos idiomas."""
    conteudo = RAIZ.read_text(encoding="utf-8")

    assert 'msgid "Brazilian Portuguese"' in conteudo
    assert 'msgid "File size must be less than %sMB"' not in conteudo


@pytest.mark.parametrize("catalogo", CATALOGOS, ids=lambda c: str(c.relative_to(settings.BASE_DIR)))
def test_catalogo_e_escrito_sem_ruido(catalogo: Path) -> None:
    """Sem `#:` (linha), sem `#~` (obsoletas) e sem data de geração."""
    linhas = catalogo.read_text(encoding="utf-8").splitlines()

    assert not [linha for linha in linhas if linha.startswith("#:")]
    assert not [linha for linha in linhas if linha.startswith("#~")]
    assert not [linha for linha in linhas if linha.startswith('"POT-Creation-Date:')]


def test_o_comando_liga_no_location_e_no_obsolete_por_padrao() -> None:
    """É o que mantém os .po legíveis -- não pode depender de lembrar da flag."""
    comando = MakeMessages()
    opcoes = comando.create_parser("manage.py", "makemessages").parse_args([])

    assert opcoes.no_location is True
    assert opcoes.no_obsolete is True


def test_traducao_do_app_resolve_em_runtime() -> None:
    if not ACCOUNTS.with_suffix(".mo").exists():
        pytest.skip("catálogo não compilado; rode `manage.py compilemessages`")

    with translation.override("pt-br"):
        assert pgettext("model", "user") == "usuário"

    with translation.override("en"):
        assert pgettext("model", "user") == "user"
