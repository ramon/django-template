"""Login do admin: valida que templates, formularios e estaticos chegam ao browser."""

from django.contrib.auth import get_user_model
from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer

# Os seletores usam name/type em vez de texto: os labels do admin sao traduzidos
# (LANGUAGE_CODE = pt-BR) e quebrariam o teste a cada mudanca de idioma.
USERNAME = "input[name='username']"
PASSWORD = "input[name='password']"
SUBMIT = "input[type='submit']"


def test_admin_login_renderiza(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/admin/login/")

    expect(page.locator(USERNAME)).to_be_visible()
    expect(page.locator(PASSWORD)).to_be_visible()
    expect(page.locator(SUBMIT)).to_be_visible()


def test_admin_login_autentica_usuario(page: Page, live_server: LiveServer) -> None:
    get_user_model().objects.create_superuser(email="admin@example.com", password="senha-forte-123")

    page.goto(f"{live_server.url}/admin/login/")
    page.locator(USERNAME).fill("admin@example.com")
    page.locator(PASSWORD).fill("senha-forte-123")
    page.locator(SUBMIT).click()

    expect(page).to_have_url(f"{live_server.url}/admin/")
    expect(page.locator("#user-tools")).to_contain_text("admin@example.com")


def test_admin_rejeita_credencial_invalida(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/admin/login/")
    page.locator(USERNAME).fill("ninguem@example.com")
    page.locator(PASSWORD).fill("senha-errada")
    page.locator(SUBMIT).click()

    expect(page).to_have_url(f"{live_server.url}/admin/login/")
    expect(page.locator(".errornote")).to_be_visible()
