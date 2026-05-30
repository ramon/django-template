from parts.django import INSTALLED_APPS
from parts.env import env

CELERY_TIMEZONE = "UTC"
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_BROKER_URL = env.cache_url("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/1")
CELERY_RESULT_BACKEND = "django-db"

INSTALLED_APPS += [
    "django_celery_results",
    "django_celery_beat"
]