"""
Signup: só a renderização do formulário estilizado.

O fluxo completo de cadastro quebra com HTTP 500 hoje, independente deste plano
de estilização (`User.REQUIRED_FIELDS` exige `first_name`/`last_name`, que o
formulário de signup do allauth nunca coleta nem preenche -- falta um
`ACCOUNT_ADAPTER` em `apps/accounts`, ver docs/plans/frontend-auth-styling.md,
etapa 9). Cobrir só a renderização até esse bug ser corrigido em outra frente.
"""

from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer


def test_signup_page_renders(page: Page, live_server: LiveServer) -> None:
    page.goto(f"{live_server.url}/auth/signup/")

    expect(page.locator("input[name='email']")).to_be_visible()
    expect(page.locator("input[name='password1']")).to_be_visible()
    expect(page.locator("input[name='password2']")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()
