from typing import Any

from apps.core.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BaseModel(UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Abstract base model providing foundational functionality for database models.

    This class serves as a base model to be inherited by other models.
    It combines features of both UUIDPrimaryKeyMixin and TimestampMixin,
    providing automatic UUID-based primary key generation and timestamp
    logging functionality. It is suitable for ensuring consistency and
    standardization across models in applications requiring these features.

    `save()` always runs `full_clean()` first, so model-level validation
    (`clean()`, field validators, uniqueness) can't be bypassed by a direct
    `.save()` call -- only `bulk_create`/`bulk_update` skip it, since those
    write straight to the database without instantiating `save()` at all; avoid
    them on models that inherit from `BaseModel`.
    """

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
