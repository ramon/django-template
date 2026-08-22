"""Signup: renderização do formulário estilizado e o fluxo completo de cadastro."""

from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer


def test_signup_page_renders(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/auth/signup/")

    expect(page.locator("input[name='name']")).to_be_visible()
    expect(page.locator("input[name='email']")).to_be_visible()
    expect(page.locator("input[name='password1']")).to_be_visible()
    expect(page.locator("input[name='password2']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


def test_signup_creates_an_account_and_asks_for_email_confirmation(
    page: Page, live_server: LiveServer
) -> None:
    page.goto(f"{live_server.url}/auth/signup/")
    page.locator("input[name='name']").fill("bea lima")
    page.locator("input[name='email']").fill("bea@example.com")
    page.locator("input[name='password1']").fill("senha-forte-123")
    page.locator("input[name='password2']").fill("senha-forte-123")
    page.locator("button[type='submit']").click()

    expect(page).to_have_url(f"{live_server.url}/auth/confirm-email/")
