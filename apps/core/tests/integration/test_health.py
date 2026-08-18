"""As sondas: o que entra na do balanceador e o que fica de fora dela."""

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_readiness_cobre_banco_cache_e_storage(client: Client) -> None:
    response = client.get(reverse("core:health_check"), {"format": "json"})

    assert response.status_code == 200
    payload = response.json()

    assert set(payload.values()) == {"OK"}, payload
    assert {
        "Database(alias='default')",
        "Cache(alias='default')",
        "Cache(alias='session')",
        "Storage(alias='default')",
    } <= set(payload)


def test_readiness_nao_depende_do_worker_do_celery(client: Client) -> None:
    """Um worker fora do ar nao pode tirar o processo web do balanceador."""
    payload = client.get(reverse("core:health_check"), {"format": "json"}).json()

    assert not any("Ping" in nome for nome in payload)


def test_sonda_dos_workers_falha_sem_worker(client: Client) -> None:
    """Sem worker respondendo ao ping, a sonda tem que acusar -- e nao mentir OK."""
    response = client.get(reverse("core:health_check_workers"), {"format": "json"})

    assert response.status_code == 500
    assert "Ping" in " ".join(response.json())
