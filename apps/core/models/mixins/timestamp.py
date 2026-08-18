from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_index=True)

    class Meta:
        abstract = True
