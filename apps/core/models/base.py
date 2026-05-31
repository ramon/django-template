from apps.core.models.mixins import UUIDPrimaryKeyMixin, TimestampMixin
from django.db import models


class AbstractBaseModel(UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Abstract base model providing foundational functionality for database models.

    This class serves as a base model to be inherited by other models.
    It combines features of both UUIDPrimaryKeyMixin and TimestampMixin,
    providing automatic UUID-based primary key generation and timestamp
    logging functionality. It is suitable for ensuring consistency and
    standardization across models in applications requiring these features.
    """
    class Meta:
        abstract = True


class AbstractSortableModel(models.Model):
    models.IntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ['sort_order',]
