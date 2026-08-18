"""A pagina inicial e' o menor caminho que exercita urls, cotton, template e assets."""

import pytest
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse

from apps.core.views import build_diagnostics

pytestmark = pytest.mark.django_db


def test_home_anuncia_que_o_app_subiu(client: Client) -> None:
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Seu app está no ar" in response.content.decode()


def test_home_resolve_o_layout_cotton(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    # <title> mora em layouts/base.html, que so e' alcancado se o componente
    # cotton <c-layouts.guest> resolveu e repassou o page_title.
    assert "<title>Seu app está no ar</title>" in body


def test_home_expoe_os_tres_frameworks_de_frontend(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    assert 'hx-get="/ping/"' in body
    assert 'data-controller="hello"' in body
    assert "x-data=" in body


@override_settings(DEBUG=True)
def test_home_mostra_o_diagnostico_em_debug(client: Client) -> None:
    body = client.get(reverse("core:home")).content.decode()

    assert "Configuração em uso" in body


def test_home_esconde_o_diagnostico_fora_de_debug(client: Client) -> None:
    """A pagina descreve a infraestrutura; isso nao pode vazar num deploy."""
    body = client.get(reverse("core:home")).content.decode()

    assert "Configuração em uso" not in body


def test_ping_devolve_o_fragmento_do_htmx(client: Client) -> None:
    response = client.get(reverse("core:ping"))

    assert response.status_code == 200
    assert "pong" in response.content.decode()


def test_diagnostico_reporta_os_settings_em_uso() -> None:
    valores = dict(build_diagnostics())

    assert valores["Settings"] == "config.settings.test"
    assert valores["Prometheus"] == "desligado"
    assert valores["Django"].startswith("6.")
