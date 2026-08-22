"""Reset de senha: renderização e o redirect para a tela de confirmação."""

from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer


def test_password_reset_page_renders(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/auth/password/reset/")

    expect(page.locator("input[name='email']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


def test_password_reset_redirects_to_done_page(page: Page, live_server: LiveServer) -> None:
    """
    allauth não revela se o e-mail existe -- redireciona para a mesma tela em
    qualquer caso, então um e-mail desconhecido basta para o teste.
    """
    page.goto(f"{live_server.url}/auth/password/reset/")
    page.locator("input[name='email']").fill("ninguem@example.com")
    page.locator("button[type='submit']").click()

    expect(page).to_have_url(f"{live_server.url}/auth/password/reset/done/")
