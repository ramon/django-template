"""The home page in a real browser: proves the Vite bundle loads and runs."""

from playwright.sync_api import Page, expect


def test_home_renders_the_announcement(e2e_page: Page) -> None:
    expect(e2e_page.locator("h1")).to_have_text("Seu app está no ar")


def test_htmx_swaps_the_server_fragment(e2e_page: Page) -> None:
    output = e2e_page.locator("#ping-output")
    expect(output).to_have_text("sem resposta ainda")

    e2e_page.get_by_role("button", name="ping").click()

    expect(output).to_contain_text("pong")


def test_stimulus_connects_the_controller(e2e_page: Page) -> None:
    e2e_page.locator("[data-hello-target='name']").fill("Ramon")
    e2e_page.get_by_role("button", name="cumprimentar").click()

    expect(e2e_page.locator("[data-hello-target='output']")).to_have_text("Ola, Ramon!")


def test_alpine_keeps_local_state(e2e_page: Page) -> None:
    counter = e2e_page.locator("[x-text='count']")
    expect(counter).to_have_text("0")

    e2e_page.get_by_role("button", name="somar").click()
    e2e_page.get_by_role("button", name="somar").click()

    expect(counter).to_have_text("2")


def test_home_does_not_expose_diagnostics_outside_debug(e2e_page: Page) -> None:
    """Test settings run with DEBUG=False, like a deploy."""
    assert "Configuração em uso" not in e2e_page.content()
