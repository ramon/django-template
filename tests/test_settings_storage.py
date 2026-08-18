"""Remote storage is optional; these tests pin down both sides of the switch."""

import importlib
from collections.abc import Iterator
from typing import Any

import pytest
from django.conf import settings

import config.settings.parts.storage as storage_part


@pytest.fixture
def reload_storage(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Reloads the part to see the effect of the environment variables.

    Settings are resolved once, at import time; without a reload there is no way
    to exercise the other branch of `if USE_S3`. The undo happens before the
    final reload so the module returns to its default state even when the test
    left USE_S3 on.
    """
    yield
    monkeypatch.undo()
    importlib.reload(storage_part)


def test_uploads_default_to_disk() -> None:
    assert settings.STORAGES["default"]["BACKEND"] == (
        "django.core.files.storage.FileSystemStorage"
    )


@pytest.mark.usefixtures("reload_storage")
def test_use_s3_swaps_the_default_backend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_S3", "True")
    monkeypatch.setenv("AWS_STORAGE_BUCKET_NAME", "meu-bucket")
    monkeypatch.setenv("AWS_S3_REGION_NAME", "sa-east-1")

    importlib.reload(storage_part)

    default: dict[str, Any] = storage_part.STORAGES["default"]
    assert default["BACKEND"] == "storages.backends.s3.S3Storage"
    assert default["OPTIONS"]["bucket_name"] == "meu-bucket"
    assert default["OPTIONS"]["region_name"] == "sa-east-1"
    # static files storage does not change: ServeStatic still serves it
    assert storage_part.STORAGES["staticfiles"]["BACKEND"].startswith("servestatic")


@pytest.mark.usefixtures("reload_storage")
def test_use_s3_requires_the_bucket_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Failing at boot is better than coming up pointing nowhere."""
    monkeypatch.setenv("USE_S3", "True")
    monkeypatch.delenv("AWS_STORAGE_BUCKET_NAME", raising=False)

    with pytest.raises(Exception, match="AWS_STORAGE_BUCKET_NAME"):
        importlib.reload(storage_part)
