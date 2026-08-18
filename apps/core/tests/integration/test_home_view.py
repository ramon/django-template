"""The home page is the smallest path that exercises urls, cotton, templates, and assets."""

import pytest
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse

from apps.core.views import build_diagnostics

pytestmark = pytest.mark.django_db


def test_home_announces_that_the_app_is_up(client: Client) -> None:
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Seu app está no ar" in response.content.decode()


def test_home_resolves_the_cotton_layout(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    # <title> lives in layouts/base.html, which is only reached if the cotton
    # <c-layouts.guest> component resolved and forwarded page_title.
    assert "<title>Seu app está no ar</title>" in body


def test_home_exposes_the_three_frontend_frameworks(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    assert 'hx-get="/ping/"' in body
    assert 'data-controller="hello"' in body
    assert "x-data=" in body


@override_settings(DEBUG=True)
def test_home_shows_diagnostics_in_debug(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    assert "Configuração em uso" in body


def test_home_hides_diagnostics_outside_debug(client: Client) -> None:
    """The page describes the infrastructure; that cannot leak in a deploy."""
    body = client.get(reverse("core:home")).content.decode()

    assert "Configuração em uso" not in body


def test_ping_returns_the_htmx_fragment(client: Client) -> None:
    response = client.get(reverse("core:ping"))

    assert response.status_code == 200
    assert "pong" in response.content.decode()


def test_diagnostics_reports_the_settings_in_use() -> None:
    values = dict(build_diagnostics())

    assert values["Settings"] == "config.settings.test"
    assert values["Prometheus"] == "desligado"
    assert values["Django"].startswith("6.")
