"""Remote storage is optional; these tests pin down both sides of the switch."""

import importlib
from collections.abc import Iterator
from typing import Any
from wsgiref.headers import Headers

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
    assert storage_part.STORAGES["staticfiles"]["BACKEND"] == (
        "apps.core.storage.ViteManifestStaticFilesStorage"
    )


@pytest.mark.usefixtures("reload_storage")
def test_use_s3_requires_the_bucket_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Failing at boot is better than coming up pointing nowhere."""
    monkeypatch.setenv("USE_S3", "True")
    monkeypatch.delenv("AWS_STORAGE_BUCKET_NAME", raising=False)

    with pytest.raises(Exception, match="AWS_STORAGE_BUCKET_NAME"):
        importlib.reload(storage_part)


def test_static_files_storage_keeps_vite_names() -> None:
    assert storage_part.STORAGES["staticfiles"]["BACKEND"] == (
        "apps.core.storage.ViteManifestStaticFilesStorage"
    )


def test_servestatic_uses_the_vite_headers_function() -> None:
    """`SERVESTATIC_IMMUTABLE_FILE_TEST` would not work: the middleware overrides it."""
    # compara pelo nome: os testes de S3 recarregam o part e trocam a identidade da funcao
    function = settings.SERVESTATIC_ADD_HEADERS_FUNCTION
    assert (function.__module__, function.__qualname__) == (
        "config.settings.parts.storage",
        "add_vite_cache_headers",
    )


@pytest.mark.parametrize(
    "url",
    [
        "/static/dist/assets/app-C7zUWH_5.js",
        "/static/dist/assets/controllers-DJpULXPU.js",
        "/static/dist/assets/app-Cd3qm70Y.css",
        "/static/dist/assets/inter-latin-wght-normal-Dx4kXJAl.woff2",
    ],
)
def test_vite_versioned_files_are_immutable(url: str) -> None:
    headers = Headers([("Cache-Control", "max-age=60, public")])

    storage_part.add_vite_cache_headers(headers, "/app/public" + url, url)

    assert headers["Cache-Control"] == "max-age=315360000, public, immutable"


@pytest.mark.parametrize(
    "url",
    [
        "/static/img/logo.svg",
        "/static/dist/.vite/manifest.json",
        "/static/dist/assets/app.js",
        "/static/assets/app-C7zUWH_5.js",
    ],
)
def test_other_files_keep_their_cache_headers(url: str) -> None:
    headers = Headers([("Cache-Control", "max-age=60, public")])

    storage_part.add_vite_cache_headers(headers, "/app/public" + url, url)

    assert headers["Cache-Control"] == "max-age=60, public"
