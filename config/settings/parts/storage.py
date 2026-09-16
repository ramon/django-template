import re
from typing import Any
from wsgiref.headers import Headers

from servestatic.base import ServeStaticBase

from config.settings.parts.env import env
from config.settings.parts.paths import PUBLIC_DIR, STATIC_DIR

# anotado porque o ramo do S3 acrescenta OPTIONS, um dict dentro do dict
STORAGES: dict[str, dict[str, Any]] = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "apps.core.storage.ViteManifestStaticFilesStorage",
    },
}

STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = PUBLIC_DIR / "static"
STATICFILES_DIRS = [STATIC_DIR]

MEDIA_URL = env("MEDIA_URL", default="/media/")
MEDIA_ROOT = PUBLIC_DIR / "media"

# Storage remoto e' opcional: sem USE_S3 os uploads ficam em disco, como acima.
# Dentro de um container o disco e' efemero, entao qualquer deploy com upload de
# usuario precisa ligar isto (e o extra: `uv sync --extra s3`).
USE_S3 = env.bool("USE_S3", default=False)

if USE_S3:
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": env.str("AWS_STORAGE_BUCKET_NAME"),
            "region_name": env.str("AWS_S3_REGION_NAME", default="us-east-1"),
            # preenchido apenas para S3 compativel (MinIO, R2, Spaces)
            "endpoint_url": env.str("AWS_S3_ENDPOINT_URL", default=None),
            # credenciais ficam com a cadeia padrao do boto3: variaveis de
            # ambiente na sua maquina, IAM role no cluster.
            "file_overwrite": False,
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": env.int("AWS_QUERYSTRING_EXPIRE", default=3600),
        },
    }

SERVESTATIC_ROOT = PUBLIC_DIR

# nome que o Vite da' ao que ele versiona: dist/assets/<nome>-<hash de 8>.<ext>
VITE_VERSIONED_URL = re.compile(r"/dist/assets/[^/]+-[\w-]{8}\.\w+$")


# `path` fica na assinatura porque o ServeStatic chama com os tres argumentos
def add_vite_cache_headers(headers: Headers, path: str, url: str) -> None:  # noqa: ARG001
    """
    Marks the files Vite versions by content as immutable.

    The storage leaves them without Django's hash (see
    `apps.core.storage.ViteManifestStaticFilesStorage`), and ServeStatic only
    recognizes Django's, so they would go out with a 60 s max-age. This is the
    hook the middleware honors: it overrides `immutable_file_test` and ignores
    `SERVESTATIC_IMMUTABLE_FILE_TEST`.

    Args:
        headers: Response headers ServeStatic built for the file, changed in place.
        path: Filesystem path of the file.
        url: Request path, including the path part of `STATIC_URL`.
    """
    if VITE_VERSIONED_URL.search(url):
        headers["Cache-Control"] = f"max-age={ServeStaticBase.FOREVER}, public, immutable"


SERVESTATIC_ADD_HEADERS_FUNCTION = add_vite_cache_headers

__all__ = [
    "MEDIA_ROOT",
    "MEDIA_URL",
    "SERVESTATIC_ADD_HEADERS_FUNCTION",
    "SERVESTATIC_ROOT",
    "STATICFILES_DIRS",
    "STATIC_ROOT",
    "STATIC_URL",
    "STORAGES",
    "USE_S3",
]
