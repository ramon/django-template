from django.utils import timezone
from django_guid.integrations import SentryIntegration, CeleryIntegration
from .django import DEBUG, INSTALLED_APPS, MIDDLEWARE
import structlog

INSTALLED_APPS += [
    "django_guid",
    "django_structlog"
]

MIDDLEWARE += [
    "django_guid.middleware.guid_middleware",
    "django_structlog.middlewares.RequestMiddleware",
]

DJANGO_GUID = {
    "GUID_HEADER_NAME": "X-Correlation-Id",
    'VALIDATE_GUID': True,
    'RETURN_HEADER': True,
    'EXPOSE_HEADER': True,
    'INTEGRATIONS': [
        SentryIntegration(),
        CeleryIntegration(
            use_django_logging=True,
            log_parent=True,
            sentry_integration=True
        )
    ],
    'IGNORE_URLS': [],
    'UUID_LENGTH': 32,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {asctime} {correlation_id} {module} {message}",
            "style": "{",
        },
        "structlog": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": "structlog.processors.JSONRenderer",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "format": '{levelname} {client_addr} {correlation_id} - "{request_line}" {status_code}',
            "style": "{",
        }
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "correlation_id": {
            "()": "django_guid.log_filters.CorrelationId"
        }
    },
    "handlers": {
        "console": {
            "()": "logging.StreamHandler",
            "formatter": "simple",
            "filters": ["correlation_id"],
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "uvicorn": {"handlers": ["console" ], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "django_guid": {
            "handlers": ["console_dev"],
            "level": "WARNING",
            "propagate": False,
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "app.events": {
            "handlers": ["events"],
            "level": "INFO",
            "propagate": False,
        }
    }
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

__all__ = ["DJANGO_GUID", "LOGGING"]
