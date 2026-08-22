"""Fixtures compartilhadas pelos testes ponta a ponta."""

import os

# A API sincrona do Playwright mantem um event loop vivo na thread do teste, e o
# Django recusa ORM sincrono nesse contexto. Aqui o acesso e' seguro: o servidor
# roda em outra thread (live_server) e cada teste e' sequencial.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from django.conf import settings
from playwright.sync_api import Page
from pytest_django.live_server_helper import LiveServer

if TYPE_CHECKING:
    from apps.accounts.models import User

# senha fixa (nao a do UserFactory) para os testes de login poderem preenche-la
# explicitamente no formulario, sem depender do valor default da factory.
VERIFIED_USER_PASSWORD = "senha-de-teste-123"  # nosec


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


@pytest.fixture
def verified_user(db: None) -> User:  # noqa: ARG001
    """
    Usuario com e-mail ja verificado no allauth (`EmailAddress.verified=True`).

    `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` bloqueia o login de quem nao tem
    isso -- o `UserFactory` sozinho nao basta, porque `EmailAddress` e' um model
    do allauth, sem relacao com o `User.objects.create_user` do projeto.
    """
    from allauth.account.models import EmailAddress

    from apps.accounts.tests.factories import UserFactory

    user = UserFactory.create(password=VERIFIED_USER_PASSWORD)
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


def login(page: Page, live_server: LiveServer, user: User) -> None:
    """Autentica `user` preenchendo o formulario real de login no browser."""
    page.goto(f"{live_server.url}/auth/login/")
    page.locator("input[name='login']").fill(user.email)
    page.locator("input[name='password']").fill(VERIFIED_USER_PASSWORD)
    # so' o botao "Entrar" -- o de passkey tambem e' type=submit, mas associado
    # a outro <form> via o atributo HTML `form=` (vive fora do <form> de login).
    page.locator("button[type='submit']:not([form])").click()
