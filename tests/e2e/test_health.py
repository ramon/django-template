"""The health check is the smallest path that exercises URLs, cache, and database end to end."""

import json

from playwright.sync_api import Page
from pytest_django.live_server_helper import LiveServer


def test_health_check_reports_everything_ok(page: Page, live_server: LiveServer) -> None:
    response = page.goto(f"{live_server.url}/health/?format=json")

    assert response is not None
    assert response.status == 200

    payload = json.loads(response.text())
    assert set(payload.values()) == {"OK"}, payload


def test_health_check_responds_in_html(e2e_page: Page, live_server: LiveServer) -> None:
    e2e_page.goto(f"{live_server.url}/health/")

    assert "Database" in e2e_page.content()
