from typing import Any, Self

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy


class SoftDeleteQuerySet(models.QuerySet["SoftDeleteModel"]):
    """
    A custom QuerySet for implementing soft delete functionality.

    This class extends the standard Django QuerySet to provide utilities for
    soft deleting objects by marking them as deleted without removing them
    from the database. It also provides methods to query alive (non-deleted)
    and dead (soft-deleted) objects.

    Methods:
        delete: Marks the objects in the queryset as deleted by setting
            the 'deleted_at' timestamp to the current time.
        hard_delete: Permanently deletes objects from the database.
        alive: Filters the queryset to include only objects that have not
            been soft deleted (i.e., 'deleted_at' is null).
        dead: Filters the queryset to include only objects that have been
            soft deleted (i.e., 'deleted_at' is not null).
    """

    # retorna int (de update()) em vez do tuple[int, dict] da base, que nao se aplica aqui
    def delete(self) -> int:  # type: ignore[override]
        return self.update(deleted_at=timezone.now())

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()

    def alive(self) -> Self:
        return self.filter(deleted_at__isnull=True)

    def dead(self) -> Self:
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager["SoftDeleteModel"]):
    """Manager for handling soft-deleted objects.

    Provides a customized queryset that excludes soft-deleted objects by
    default. This manager can be used to implement soft-deletion logic
    across models, enabling filtering of only active (non-deleted) records.

    Attributes:
        model (type): The model class this manager is attached to.
        _db (type): The database being used with this manager.
    """

    def get_queryset(self) -> SoftDeleteQuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class SoftDeleteModel(models.Model):
    """
    Provides a mixin for implementing soft delete functionality in Django models.

    SoftDeleteMixin allows for marking an object as deleted by setting a timestamp in the
    `deleted_at` field instead of permanently removing the object from the database. This approach
    supports features such as data recovery and audit trails.

    Attributes:
        deleted_at (datetime): The timestamp indicating when the object was soft-deleted. If `None`,
            the object is considered active.

        objects (SoftDeleteManager): Custom manager providing access to only active (non-deleted) objects.

        all_objects (models.Manager): Default manager providing access to all objects, including
            those that are soft-deleted.
    """

    deleted_at = models.DateTimeField(
        gettext_lazy("deleted at"), null=True, blank=True, db_index=True
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager["SoftDeleteModel"]()

    class Meta:
        abstract = True

    # retorna None em vez do tuple[int, dict] da base: soft delete nao apaga nada para contar
    def delete(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        """
        Marks the instance as deleted by setting the `deleted_at` field to the current
        timestamp.
        """
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args: Any, **kwargs: Any) -> None:
        """
        Permanently deletes an instance from the database.

        This method overrides the default deletion behavior to ensure the instance
        is permanently removed, bypassing any soft delete mechanism if present.
        """
        super().delete(*args, **kwargs)

    def restore(self) -> None:
        """
        Restores a previously soft-deleted object.

        This method reverts the soft-delete operation by setting the `deleted_at`
        attribute to `None` and saving the object. It ensures that the object's
        soft-deleted state is removed and it becomes active again.

        Returns:
            None: This method does not return any value.
        """
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self) -> bool:
        """
        Checks if the object has been marked as deleted based on the presence of a deletion timestamp.

        Returns:
            bool: True if the object has been marked as deleted (deleted_at is not None), False otherwise.
        """
        return self.deleted_at is not None
