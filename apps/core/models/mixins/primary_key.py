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
        id: The primary key field for the model, represented as a UUID.
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid7)

    class Meta:
        abstract = True
