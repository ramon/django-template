from django.db import models


class SortableMixin(models.Model):
    """
    Provides sorting functionality for models.

    This mixin is an abstract base class designed to add sorting capabilities to
    your Django models by including a `sort_order` field. The `sort_order` field
    is an integer field that can be used for ordering instances of this model.
    Additionally, it sets a default ordering based on the `sort_order` field.

    Attributes:
        sort_order (IntegerField): Defines the order in which instances of this
            model should be sorted. Defaults to 0 and is indexed for efficient
            queries.
    """

    sort_order = models.IntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = [
            "sort_order",
        ]
