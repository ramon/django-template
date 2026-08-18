from django.db import models
from django.utils.functional import cached_property

from apps.core.domain import PersonName


class PersonNameMixin(models.Model):
    """
    Mixin class for representing a person's name.

    This class provides attributes and methods for managing a person's first and
    last name. It includes a cached property for optimized name handling and a
    custom setter for updating the name while maintaining a consistent internal
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

        This method splits the provided full name into first and last names by using
        the `PersonName` utility. It also clears the cached name attribute if it exists
        to ensure correctness for later name operations.

        Args:
            full_name: The full name of the individual as a single string. This should
                include both the first name and last name separated by a space.
        """
        name = PersonName.from_full_name(full_name)
        self.first_name = name.first
        self.last_name = name.last

        self.__dict__.pop("_cached_name", None)  # expira o cache
