"""MFA: index sem autenticador, ativação de TOTP e códigos de recuperação."""

import base64
import hashlib
import hmac
import struct
import time

from playwright.sync_api import Page, expect
from pytest_django.live_server_helper import LiveServer

from apps.accounts.models import User
from tests.e2e.conftest import login

TOTP_ACTIVATE_URL = "/auth/2fa/totp/activate/"


def _totp_code(secret: str) -> str:
    """
    Calcula o código TOTP (RFC 6238) atual a partir do segredo em base32.

    Evita depender de uma lib externa (ex. pyotp) só para o teste "digitar"
    um código válido no formulário real de ativação.
    """
    key = base64.b32decode(secret, casefold=True)
    counter = int(time.time()) // 30
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def test_mfa_index_offers_to_activate_totp(
    page: Page, live_server: LiveServer, verified_user: User
) -> None:
    login(page, live_server, verified_user)

    page.goto(f"{live_server.url}/auth/2fa/")

    expect(page.locator(f"a[href='{TOTP_ACTIVATE_URL}']")).to_be_visible()


def test_activating_totp_generates_recovery_codes(
    page: Page, live_server: LiveServer, verified_user: User
) -> None:
    login(page, live_server, verified_user)

    page.goto(f"{live_server.url}{TOTP_ACTIVATE_URL}")
    secret = page.locator("#authenticator_secret").input_value()
    page.locator("#id_code").fill(_totp_code(secret))
    page.locator("button[type='submit']").click()

    expect(page).to_have_url(f"{live_server.url}/auth/2fa/recovery-codes/")
    expect(page.locator("#recovery_codes")).to_be_visible()
    expect(page.locator("a[href='/auth/2fa/recovery-codes/download/']")).to_be_visible()
