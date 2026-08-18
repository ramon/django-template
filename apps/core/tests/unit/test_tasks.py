"""The example task, run in eager mode (no broker, no worker)."""

from collections.abc import Iterator

import pytest
from celery import current_app

from apps.core.tasks import echo


@pytest.fixture
def sync_queue() -> Iterator[None]:
    """Runs tasks in the current process instead of publishing to the broker."""
    previous = current_app.conf.task_always_eager
    current_app.conf.task_always_eager = True
    yield
    current_app.conf.task_always_eager = previous


def test_echo_returns_the_message() -> None:
    assert echo("ola") == "ola"


@pytest.mark.usefixtures("sync_queue")
def test_echo_runs_through_the_celery_path() -> None:
    """Proves the task is registered and that .delay reaches it, without needing a broker."""
    result = echo.delay("ola")

    assert result.successful()
    assert result.get() == "ola"


def test_the_task_is_registered_under_its_declared_name() -> None:
    """The autodiscover finds tasks.py in every installed app."""
    assert "core.echo" in current_app.tasks
