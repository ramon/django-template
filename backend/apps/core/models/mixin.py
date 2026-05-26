import uuid
from functools import cached_property

from django.db import models

from apps.core.value_objects.person_name import PersonName


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
    """
    Mixin class for representing a person's name.

    This class provides attributes and methods for managing a person's first and
    last name. It includes a cached property for optimized name handling and a
    custom setter for updating the name while maintaining consistent internal
    state.

    Attributes:
        first_name (str): The first name of the person.
        last_name (str): The last name of the person.
    """
    first_name: str = models.CharField(max_length=255)
    last_name: str = models.CharField(max_length=255)

    class Meta:
        abstract = True

    @cached_property
    def _cached_name(self) -> PersonName:
        """
        Returns the cached full name of the person as a `PersonName` object.

        This method provides a cached computation of the full name by combining the
        `first_name` and `last_name` attributes.

        Returns:
            PersonName: The full name representation of the person.
        """
        return PersonName(first=self.first_name, last=self.last_name)

    @property
    def name(self) -> PersonName:
        """
        Gets the name of the person as a `PersonName` object.

        This property retrieves the cached name value of the person, represented
        as an instance of the `PersonName` class. The cached name is stored
        internally and returned upon access.

        Returns:
            PersonName: The cached name of the person.
        """
        return self._cached_name

    @name.setter
    def name(self, full_name: str) -> None:
        """
        Setter method for updating the individual's full name.

        This method splits the provided full name into first and last names by utilizing
        the `PersonName` utility. It also clears the cached name attribute if it exists
        to ensure correctness for subsequent name operations.

        Args:
            full_name: The full name of the individual as a single string. This should
                include both the first name and last name separated by a space.
        """
        name = PersonName.from_full_name(full_name)
        self.first_name = name.first
        self.last_name = name.last

        self.__dict__.pop("_cached_name", None) # expira o cache
