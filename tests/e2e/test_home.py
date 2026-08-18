"""A pagina inicial num browser real: prova que o bundle do Vite carrega e roda."""

from playwright.sync_api import Page, expect


def test_home_renderiza_o_anuncio(e2e_page: Page) -> None:
    expect(e2e_page.locator("h1")).to_have_text("Seu app está no ar")


def test_htmx_troca_o_fragmento_do_servidor(e2e_page: Page) -> None:
    saida = e2e_page.locator("#ping-output")
    expect(saida).to_have_text("sem resposta ainda")

    e2e_page.get_by_role("button", name="ping").click()

    expect(saida).to_contain_text("pong")


def test_stimulus_conecta_o_controller(e2e_page: Page) -> None:
    e2e_page.locator("[data-hello-target='name']").fill("Ramon")
    e2e_page.get_by_role("button", name="cumprimentar").click()

    expect(e2e_page.locator("[data-hello-target='output']")).to_have_text("Ola, Ramon!")


def test_alpine_mantem_estado_local(e2e_page: Page) -> None:
    contador = e2e_page.locator("[x-text='count']")
    expect(contador).to_have_text("0")

    e2e_page.get_by_role("button", name="somar").click()
    e2e_page.get_by_role("button", name="somar").click()

    expect(contador).to_have_text("2")


def test_home_nao_expoe_o_diagnostico_fora_de_debug(e2e_page: Page) -> None:
    """Os settings de teste rodam com DEBUG=False, como um deploy."""
    assert "Configuração em uso" not in e2e_page.content()
