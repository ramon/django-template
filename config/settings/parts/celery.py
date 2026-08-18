from .django import INSTALLED_APPS
from .env import env

INSTALLED_APPS += ["django_celery_results", "django_celery_beat"]

# env.cache_url devolve um dict de CACHES; o Celery espera a URL crua.
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/2")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_ACCEPT_CONTENT = ["application/json"]
# "orjson" nao existe no registro do kombu -- com ele o worker morre no boot com
# KeyError. E nao adianta registrar: o kombu envelopa Decimal, datetime e bytes em
# {"__type__", "__value__"} e desfaz isso com um object_hook, que o orjson nao
# suporta. O orjson fica onde rende de fato, no renderer da API (config/urls/api.py).
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TIME_LIMIT = 5 * 60

__all__ = [
    "CELERY_ACCEPT_CONTENT",
    "CELERY_BEAT_SCHEDULER",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "CELERY_RESULT_EXTENDED",
    "CELERY_RESULT_SERIALIZER",
    "CELERY_TASK_SERIALIZER",
    "CELERY_TASK_TIME_LIMIT",
    "CELERY_TIMEZONE",
]
