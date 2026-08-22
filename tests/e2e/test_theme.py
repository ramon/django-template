"""Dark mode toggle: classe `.dark`, persistência e reaplicação sem flash."""

from playwright.sync_api import Page, expect


def test_theme_toggle_switches_to_dark(e2e_page: Page) -> None:
    html = e2e_page.locator("html")
    expect(html).not_to_have_class("dark")

    e2e_page.get_by_role("button", name="Alternar tema claro/escuro").click()

    expect(html).to_have_class("dark")
    assert e2e_page.evaluate("localStorage.getItem('theme')") == "dark"


def test_theme_choice_survives_a_reload(e2e_page: Page) -> None:
    e2e_page.get_by_role("button", name="Alternar tema claro/escuro").click()
    expect(e2e_page.locator("html")).to_have_class("dark")

    e2e_page.reload()

    expect(e2e_page.locator("html")).to_have_class("dark")


def test_theme_toggle_switches_back_to_light(e2e_page: Page) -> None:
    toggle = e2e_page.get_by_role("button", name="Alternar tema claro/escuro")
    html = e2e_page.locator("html")

    toggle.click()
    expect(html).to_have_class("dark")

    toggle.click()

    expect(html).not_to_have_class("dark")
    assert e2e_page.evaluate("localStorage.getItem('theme')") == "light"
