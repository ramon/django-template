from .django import INSTALLED_APPS
from .env import env

INSTALLED_APPS += [
    "django_celery_results",
    "django_celery_beat"
]

CELERY_BROKER_URL = env.cache_url("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/1")
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "orjson"
CELERY_RESULT_SERIALIZER  = "orjson"
CELERY_RESULT_BACKEND = "django-db"
CELERY_RESULT_EXTENDED = True
CELERY_TIMEZONE = "UTC"
CELERY_TASK_TIME_LIMIT = 5 * 60

__all__ = [
    "CELERY_BROKER_URL",
    "CELERY_BEAT_SCHEDULER",
    "CELERY_ACCEPT_CONTENT",
    "CELERY_TASK_SERIALIZER",
    "CELERY_RESULT_SERIALIZER",
    "CELERY_RESULT_BACKEND",
    "CELERY_RESULT_EXTENDED",
    "CELERY_TIMEZONE",
    "CELERY_TASK_TIME_LIMIT",
]