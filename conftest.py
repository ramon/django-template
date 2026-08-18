"""Fixtures compartilhadas por toda a suite."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client

if TYPE_CHECKING:
    from apps.accounts.models import User

# manifest minimo, com a mesma forma que o Vite gera: chave = input relativo a' raiz.
STUB_MANIFEST: dict[str, Any] = {
    "frontend/entries/app.js": {
        "file": "assets/app.stub.js",
        "css": ["assets/app.stub.css"],
    },
}


@pytest.fixture(scope="session", autouse=True)
def vite_manifest_stub() -> Iterator[None]:
    """
    Permite renderizar templates sem ter rodado `bun run build`.

    Fora de DEBUG -- o caso dos settings de teste -- os templatetags resolvem os
    assets pelo manifest do Vite, entao qualquer teste que renderize uma pagina
    dependeria do build do frontend. Os testes de unidade nao devem exigir a
    toolchain de JS; quando o build existe de verdade, ele e' usado como esta.
    """
    from apps.core.templatetags import vite

    if vite._manifest_path().exists():
        yield
        return

    original = vite._load_manifest
    vite._load_manifest = lambda: STUB_MANIFEST  # type: ignore[assignment]
    try:
        yield
    finally:
        vite._load_manifest = original


# As factories importam models, que exigem o Django ja configurado. Este conftest
# e' carregado antes disso, entao o import mora dentro de cada fixture.


@pytest.fixture
def user(db: None) -> User:  # noqa: ARG001 -- `db` da acesso ao banco por efeito colateral
    """Usuario comum, ja com Profile (o create_user cuida disso)."""
    from apps.accounts.tests.factories import UserFactory

    return UserFactory.create()


@pytest.fixture
def superuser(db: None) -> User:  # noqa: ARG001
    from apps.accounts.tests.factories import SuperUserFactory

    return SuperUserFactory.create()


@pytest.fixture
def auth_client(client: Client, user: User) -> Client:
    """Test client autenticado como `user`."""
    client.force_login(user)
    return client
