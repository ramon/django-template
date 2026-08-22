"""Login: renderização do formulário estilizado e autenticação real."""

from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer

from apps.accounts.models import User
from tests.e2e.conftest import login


def test_login_page_renders(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/auth/login/")

    expect(page.locator("input[name='login']")).to_be_visible()
    expect(page.locator("input[name='password']")).to_be_visible()
    # so' o botao "Entrar" -- o de passkey tambem e' type=submit, mas associado
    # a outro <form> via o atributo HTML `form=`.
    expect(page.locator("button[type='submit']:not([form])")).to_be_visible()


def test_login_authenticates_a_verified_user(
    page: Page, live_server: LiveServer, verified_user: User
) -> None:
    login(page, live_server, verified_user)

    expect(page).to_have_url(live_server.url + "/")


def test_login_rejects_wrong_password(
    page: Page, live_server: LiveServer, verified_user: User
) -> None:
    page.goto(f"{live_server.url}/auth/login/")
    page.locator("input[name='login']").fill(verified_user.email)
    page.locator("input[name='password']").fill("senha-errada")
    page.locator("button[type='submit']:not([form])").click()

    expect(page).to_have_url(f"{live_server.url}/auth/login/")
    expect(page.get_by_role("alert")).to_be_visible()
