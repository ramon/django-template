"""A task de exemplo, executada em modo eager (sem broker nem worker)."""

from collections.abc import Iterator

import pytest
from celery import current_app

from apps.core.tasks import echo


@pytest.fixture
def fila_sincrona() -> Iterator[None]:
    """Executa as tasks no proprio processo, em vez de publicar no broker."""
    anterior = current_app.conf.task_always_eager
    current_app.conf.task_always_eager = True
    yield
    current_app.conf.task_always_eager = anterior


def test_echo_devolve_a_mensagem() -> None:
    assert echo("ola") == "ola"


@pytest.mark.usefixtures("fila_sincrona")
def test_echo_roda_pelo_caminho_do_celery() -> None:
    """Prova que a task esta registrada e que .delay a alcanca, sem exigir broker."""
    resultado = echo.delay("ola")

    assert resultado.successful()
    assert resultado.get() == "ola"


def test_a_task_esta_registrada_com_o_nome_declarado() -> None:
    """O autodiscover encontra tasks.py de cada app instalado."""
    assert "core.echo" in current_app.tasks
