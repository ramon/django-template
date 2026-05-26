import uuid

from django.db import models


class UUIDPrimaryKeyMixin(models.Model):
    """
    A mixin to add a UUID primary key to a model.

    This mixin provides a model with a primary key field of type UUID, ensuring
    each instance has a unique identifier. The UUID is auto-generated using the
    UUID version 7 algorithm, which offers time-ordered, unique, and efficient
    UUID generation. This class is intended to be used as an abstract base class
    for models requiring this functionality.

    Attributes:
        id (UUIDField): The primary key field for the model, represented as a UUID.
    """
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid7)

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    """
    Mixin class providing created and updated timestamp fields for a Django model.

    This abstract mixin class is designed to be inherited by other Django models to automatically
    include `created_at` and `updated_at` fields. These fields track the creation and last update
    times of the model instance, respectively. The `created_at` field is set only once at the time
    of creation, while the `updated_at` field updates automatically whenever the model instance is
    modified.

    Attributes:
        created_at (datetime): The timestamp indicating when the model instance was created.
        updated_at (datetime): The timestamp indicating the last time the model instance was updated.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        db_index=True
    )

    class Meta:
        abstract = True


class PersonNameMixin(models.Model):
    first_name: str = models.CharField(max_length=255)
    last_name: str = models.CharField(max_length=255)

    class Meta:
        abstract = True
