"""Fixtures compartilhadas pelos testes ponta a ponta."""

import os

# A API sincrona do Playwright mantem um event loop vivo na thread do teste, e o
# Django recusa ORM sincrono nesse contexto. Aqui o acesso e' seguro: o servidor
# roda em outra thread (live_server) e cada teste e' sequencial.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from collections.abc import Iterator
from pathlib import Path

import pytest
from django.conf import settings
from playwright.sync_api import Page
from pytest_django.live_server_helper import LiveServer


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Marca todo teste deste pacote como e2e e libera o acesso ao banco.

    Evita repetir `pytestmark` em cada modulo -- estar em tests/e2e/ ja define o
    que o teste e'. (pytestmark num conftest nao tem efeito sobre os modulos.)
    """
    package_root = Path(__file__).parent

    for item in items:
        if package_root in Path(str(item.fspath)).parents:
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.django_db)


@pytest.fixture(scope="session", autouse=True)
def vite_manifest() -> None:
    """
    Garante que o build do frontend existe.

    Os templates resolvem CSS e JS pelo manifest do Vite quando DEBUG e' False,
    que e' o caso nos settings de teste. Sem o build, toda pagina quebraria com
    um erro de arquivo inexistente, dificil de ligar a' causa.
    """
    manifest = Path(settings.BASE_DIR) / "static" / "dist" / ".vite" / "manifest.json"

    if not manifest.exists():
        pytest.skip(
            f"manifest do Vite nao encontrado em {manifest}. Rode `bun run build` antes dos e2e.",
            allow_module_level=True,
        )


@pytest.fixture
def e2e_page(page: Page, live_server: LiveServer) -> Iterator[Page]:
    """
    Page do Playwright ja apontando para o servidor de teste do Django.

    `live_server` sobe a aplicacao numa porta real e serve os arquivos estaticos.
    """
    page.set_default_timeout(5_000)
    page.goto(live_server.url)

    yield page
