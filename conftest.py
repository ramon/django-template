"""Fixtures compartilhadas por toda a suite."""

import contextlib
import io
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from django.test import Client

if TYPE_CHECKING:
    from collections.abc import Callable

    from playwright.sync_api import Page
    from pytest_django.live_server_helper import LiveServer

    from apps.accounts.models import User


def _is_e2e_path(path: Path) -> bool:
    """
    True para teste em qualquer `tests/e2e/` -- na raiz ou dentro de um app.

    `tests/e2e/` na raiz guarda fluxo de browser que atravessa mais de um app;
    fluxo preso a um unico app vive em `apps/<app>/tests/e2e/`. Os dois lugares
    valem, e estar no diretorio ja define o que o teste e'.
    """
    parts = path.parts
    return "e2e" in parts and "tests" in parts[: parts.index("e2e")]


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Marca todo teste sob um `tests/e2e/` como `e2e` e libera o banco."""
    for item in items:
        if _is_e2e_path(Path(str(item.fspath))):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.django_db)


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Pre-condicoes dos e2e: ORM sincrono liberado e build do frontend presente."""
    if "e2e" not in item.keywords:
        return

    # A API sincrona do Playwright mantem um event loop vivo na thread do teste, e
    # o Django recusa ORM sincrono nesse contexto. Aqui e' seguro: o servidor roda
    # noutra thread (live_server) e cada teste e' sequencial.
    os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

    # Fora de DEBUG -- o caso dos settings de teste -- os templates resolvem CSS e
    # JS pelo manifest do Vite. Sem o build, toda pagina quebraria com um erro de
    # arquivo inexistente, dificil de ligar a' causa; pular diz o que rodar.
    from apps.core.templatetags import vite

    if not vite._manifest_path().exists():
        pytest.skip("manifest do Vite ausente -- rode `bun run build` antes dos e2e")


# Pisos de cobertura em `apps/`, no mesmo espirito do `coverage.thresholds` do
# vitest.config.mjs -- linhas e branches avaliados em separado, sobre o total
# agregado do projeto (nao arquivo a arquivo: modulo fino como `core/tasks.py`
# nao precisa carregar o piso sozinho).
COVERAGE_FLOORS = {
    "percent_statements_covered": ("linhas", 90.0),
    "percent_branches_covered": ("branches", 85.0),
}


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:  # noqa: ARG001
    """
    Falha a suite se a cobertura global cair abaixo do piso, linha e branch em separado.

    `--cov-fail-under` do pytest-cov compara um numero so, que mistura linha e
    branch numa media ponderada pelo total de cada (ver `coverage.results.Numbers`) --
    nao da pra expressar "90% de linha E 85% de branch" com ele. Aqui lemos o mesmo
    `Coverage` que o pytest-cov ja rodou nesta sessao (via `--cov`) e comparamos os
    dois percentuais que o proprio relatorio json do coverage.py calcula em separado,
    sem rodar `coverage` de novo por fora do pytest.
    """
    config = session.config
    cov_plugin = config.pluginmanager.get_plugin("_cov")
    if cov_plugin is None or cov_plugin.cov_controller is None:
        return  # rodou sem --cov (ex.: `make test` local, iteracao rapida)

    # `outfile` do coverage.py so aceita path (ou "-" para stdout, ver
    # `coverage.report_core.render_report`) -- nao da pra passar um StringIO direto.
    report = io.StringIO()
    with contextlib.redirect_stdout(report):
        cov_plugin.cov_controller.cov.json_report(outfile="-", ignore_errors=True)
    totals = json.loads(report.getvalue())["totals"]

    failures = [
        f"cobertura de {label} abaixo do piso: {totals[key]:.2f}% < {floor}%"
        for key, (label, floor) in COVERAGE_FLOORS.items()
        if totals[key] < floor
    ]
    if not failures:
        return

    reporter = config.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        reporter.write_sep("-", "cobertura abaixo do piso", red=True, bold=True)
        for line in failures:
            reporter.write_line(line, red=True, bold=True)

    # `session.exitstatus` ainda esta' mutavel neste hook -- e' o mesmo mecanismo
    # que o proprio pytest-cov usa (via `session.testsfailed`) para forcar o
    # EXIT_TESTSFAILED sem lançar excecao no meio da sessao.
    session.exitstatus = pytest.ExitCode.TESTS_FAILED


# manifest minimo, com a mesma forma que o Vite gera: chave = input relativo a' raiz.
STUB_MANIFEST: dict[str, Any] = {
    "frontend/entries/app.js": {
        "file": "assets/app.stub.js",
        "css": ["assets/app.stub.css"],
    },
}


@pytest.fixture(scope="session", autouse=True)
def vite_manifest_stub() -> Iterator[None]:
    """
    Permite renderizar templates sem ter rodado `bun run build`.

    Fora de DEBUG -- o caso dos settings de teste -- os templatetags resolvem os
    assets pelo manifest do Vite, entao qualquer teste que renderize uma pagina
    dependeria do build do frontend. Os testes de unidade nao devem exigir a
    toolchain de JS; quando o build existe de verdade, ele e' usado como esta.
    """
    from apps.core.templatetags import vite

    if vite._manifest_path().exists():
        yield
        return

    original = vite._load_manifest
    vite._load_manifest = lambda: STUB_MANIFEST  # type: ignore[assignment]
    try:
        yield
    finally:
        vite._load_manifest = original


# As factories importam models, que exigem o Django ja configurado. Este conftest
# e' carregado antes disso, entao o import mora dentro de cada fixture.


@pytest.fixture
def user(db: None) -> User:  # noqa: ARG001 -- `db` da acesso ao banco por efeito colateral
    """Usuario comum, ja com Profile (o create_user cuida disso)."""
    from apps.accounts.tests.factories import UserFactory

    return UserFactory.create()


@pytest.fixture
def superuser(db: None) -> User:  # noqa: ARG001
    from apps.accounts.tests.factories import SuperUserFactory

    return SuperUserFactory.create()


@pytest.fixture
def auth_client(client: Client, user: User) -> Client:
    """Test client autenticado como `user`."""
    client.force_login(user)
    return client


# --- Ponta a ponta -----------------------------------------------------------
# Globais de proposito: servem tanto ao fluxo cross-app de `tests/e2e/` quanto
# aos e2e de um app so (`apps/<app>/tests/e2e/`). Instanciadas so quando pedidas.

# senha fixa (nao a do UserFactory) para os testes de login preenche-la
# explicitamente no formulario.
_VERIFIED_USER_PASSWORD = "senha-de-teste-123"  # nosec


@pytest.fixture
def e2e_page(page: Page, live_server: LiveServer) -> Iterator[Page]:
    """
    Page do Playwright ja apontando para o servidor de teste do Django.

    `live_server` sobe a aplicacao numa porta real e serve os arquivos estaticos.
    """
    page.set_default_timeout(5_000)
    page.goto(live_server.url)

    yield page


@pytest.fixture
def verified_user(db: None) -> User:  # noqa: ARG001
    """
    Usuario com e-mail ja verificado no allauth (`EmailAddress.verified=True`).

    `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` bloqueia o login de quem nao tem
    isso -- o `UserFactory` sozinho nao basta, porque `EmailAddress` e' um model
    do allauth, sem relacao com o `User.objects.create_user` do projeto.
    """
    from allauth.account.models import EmailAddress

    from apps.accounts.tests.factories import UserFactory

    user = UserFactory.create(password=_VERIFIED_USER_PASSWORD)
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


@pytest.fixture
def login() -> Callable[[Page, LiveServer, User], None]:
    """Helper que autentica `user` preenchendo o formulario real de login."""

    def _login(page: Page, live_server: LiveServer, user: User) -> None:
        page.goto(f"{live_server.url}/auth/login/")
        page.locator("input[name='login']").fill(user.email)
        page.locator("input[name='password']").fill(_VERIFIED_USER_PASSWORD)
        # so' o botao "Entrar" -- o de passkey tambem e' type=submit, mas associado
        # a outro <form> via o atributo HTML `form=` (vive fora do <form> de login).
        page.locator("button[type='submit']:not([form])").click()

    return _login
