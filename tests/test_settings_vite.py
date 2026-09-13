"""The browser asks the Vite dev server for assets at this URL; these tests pin
down where it comes from, so the tag and `vite.config.mjs` agree on the port."""

import importlib
from collections.abc import Iterator

import pytest

import config.settings.parts.vite as vite_part


@pytest.fixture(autouse=True)
def reload_vite(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Reloads the part to see the effect of the environment variables.

    Settings are resolved once, at import time. `parts/env.py` already copied the
    local `.env` into the environment, so both variables are cleared first to keep
    it out of the defaults under test.
    """
    monkeypatch.delenv("VITE_PORT", raising=False)
    monkeypatch.delenv("VITE_DEV_SERVER_URL", raising=False)
    yield
    monkeypatch.undo()
    importlib.reload(vite_part)


def test_dev_server_url_defaults_to_port_8001() -> None:
    importlib.reload(vite_part)

    assert vite_part.VITE_DEV_SERVER_URL == "http://127.0.0.1:8001"


def test_dev_server_url_follows_vite_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """VITE_PORT is the same variable the compose publishes and vite.config.mjs
    listens on: changing it in `.env` moves all three together."""
    monkeypatch.setenv("VITE_PORT", "8011")

    importlib.reload(vite_part)

    assert vite_part.VITE_DEV_SERVER_URL == "http://127.0.0.1:8011"


def test_explicit_dev_server_url_wins_over_vite_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VITE_PORT", "8011")
    monkeypatch.setenv("VITE_DEV_SERVER_URL", "http://vite.localhost:9000")

    importlib.reload(vite_part)

    assert vite_part.VITE_DEV_SERVER_URL == "http://vite.localhost:9000"
