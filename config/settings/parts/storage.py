from typing import Any

from config.settings.parts.env import env
from config.settings.parts.paths import PUBLIC_DIR, STATIC_DIR

# anotado porque o ramo do S3 acrescenta OPTIONS, um dict dentro do dict
STORAGES: dict[str, dict[str, Any]] = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "servestatic.storage.CompressedManifestStaticFilesStorage",
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

__all__ = [
    "MEDIA_ROOT",
    "MEDIA_URL",
    "SERVESTATIC_ROOT",
    "STATICFILES_DIRS",
    "STATIC_ROOT",
    "STATIC_URL",
    "STORAGES",
    "USE_S3",
]
