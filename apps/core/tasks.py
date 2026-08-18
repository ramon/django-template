"""
Tasks do app core.

O autodiscover do Celery procura por `tasks.py` em cada app instalado
(config/celery.py), entao basta o modulo existir aqui para a task ser
registrada. Este arquivo serve de modelo -- troque pela primeira task real.
"""

import structlog
from celery import shared_task

logger = structlog.get_logger("app.events")


@shared_task(name="core.echo")
def echo(mensagem: str) -> str:
    """
    Task minima, para verificar que a fila esta viva de ponta a ponta.

    Use `shared_task`, e nao `@app.task`: assim o modulo nao precisa importar a
    instancia do Celery e continua importavel em qualquer contexto.
    """
    logger.info("core.echo", mensagem=mensagem)
    return mensagem
