"""Fixtures compartilhadas por toda a suite."""

from collections.abc import Iterator
from typing import Any

import pytest

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
