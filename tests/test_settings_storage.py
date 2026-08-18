"""O storage remoto e' opcional; estes testes fixam os dois lados do interruptor."""

import importlib
from collections.abc import Iterator
from typing import Any

import pytest
from django.conf import settings

import config.settings.parts.storage as storage_part


@pytest.fixture
def recarrega_storage(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """
    Recarrega o part para ver o efeito das variaveis de ambiente.

    Settings sao resolvidos uma vez, no import; sem recarregar nao da para
    exercitar o outro ramo do `if USE_S3`. O undo vem antes do reload final para
    o modulo voltar ao estado padrao mesmo quando o teste deixou USE_S3 ligado.
    """
    yield
    monkeypatch.undo()
    importlib.reload(storage_part)


def test_por_padrao_os_uploads_ficam_em_disco() -> None:
    assert settings.STORAGES["default"]["BACKEND"] == (
        "django.core.files.storage.FileSystemStorage"
    )


@pytest.mark.usefixtures("recarrega_storage")
def test_use_s3_troca_o_backend_padrao(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_S3", "True")
    monkeypatch.setenv("AWS_STORAGE_BUCKET_NAME", "meu-bucket")
    monkeypatch.setenv("AWS_S3_REGION_NAME", "sa-east-1")

    importlib.reload(storage_part)

    default: dict[str, Any] = storage_part.STORAGES["default"]
    assert default["BACKEND"] == "storages.backends.s3.S3Storage"
    assert default["OPTIONS"]["bucket_name"] == "meu-bucket"
    assert default["OPTIONS"]["region_name"] == "sa-east-1"
    # o storage de estaticos nao muda: quem entrega e' o ServeStatic
    assert storage_part.STORAGES["staticfiles"]["BACKEND"].startswith("servestatic")


@pytest.mark.usefixtures("recarrega_storage")
def test_use_s3_exige_o_nome_do_bucket(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falhar no boot e' melhor que subir apontando para lugar nenhum."""
    monkeypatch.setenv("USE_S3", "True")
    monkeypatch.delenv("AWS_STORAGE_BUCKET_NAME", raising=False)

    with pytest.raises(Exception, match="AWS_STORAGE_BUCKET_NAME"):
        importlib.reload(storage_part)
