"""The probes: what belongs in the load balancer's and what stays out of it."""

import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_readiness_covers_database_cache_and_storage(client: Client) -> None:
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


def test_readiness_does_not_depend_on_the_celery_worker(client: Client) -> None:
    """A worker that's down cannot pull the web process out of the load balancer."""
    payload = client.get(reverse("core:health_check"), {"format": "json"}).json()

    assert not any("Ping" in name for name in payload)


def test_workers_probe_fails_without_a_worker(client: Client) -> None:
    """With no worker answering the ping, the probe must report it -- never a false OK."""
    response = client.get(reverse("core:health_check_workers"), {"format": "json"})

    assert response.status_code == 500
    assert "Ping" in " ".join(response.json())
