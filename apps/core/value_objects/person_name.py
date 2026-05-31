import re
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, AfterValidator, computed_field


def _normalize_name(name: str) -> str:
    """
    Normalizes a given name by removing leading and trailing spaces and converting it to title case.

    This function ensures that the input string is properly formatted by applying standard
    title-casing rules, which capitalize the first letter of each word while converting the
    remaining letters to lowercase.

    Args:
        name: The input string to be normalized.

    Returns:
        str: The normalized name with leading and trailing spaces removed and converted
        to title case.
    """
    return name.strip().title()


type NamePart = Annotated[str, Field(min_length=1, max_length=120), AfterValidator(_normalize_name)]


class PersonName(BaseModel):
    """
    Represents a person's name with various computed properties and methods.

    This class is used to model a person's name by splitting it into first and last parts,
    and provides additional computed properties such as full name, familiar name format,
    abbreviated name format, and a sorted name format for flexible usage in different contexts.

    Attributes:
        first (NamePart): The first name of the person.
        last (NamePart): The last name of the person.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    first: NamePart
    last: NamePart

    @classmethod
    def from_full_name(cls, full_name: str) -> Self:
        """
        Creates an instance of the class by parsing a full name into first and last names.

        Args:
            full_name (str): The full name consisting of a first name and a last name,
                separated by a space. It should not contain leading or trailing whitespace.

        Returns:
            Self: An instance of the class initialized with the parsed first and last names.

        Raises:
            ValueError: If the `full_name` does not contain exactly one space separating
                the first name and the last name.
        """
        first_name, last_name = full_name.strip().split(" ", 1)
        return cls(first=first_name, last=last_name)

    @computed_field
    @property
    def full(self) -> str:
        """Returns first + last, such as "Jason Fried"."""
        return f"{self.first} {self.last}"

    @computed_field
    @property
    def familiar(self) -> str:
        """Returns first + last initial, such as "Jason F."."""
        return f"{self.first} {self.last[0]}"

    @computed_field
    @property
    def abbreviated(self) -> str:
        """Returns first initial + last, such as "J. Fried"."""
        return f"{self.first[0]}. {self.last}"

    @computed_field
    @property
    def sorted(self) -> str:
        """Returns last + first for sorting."""
        return f"{self.last}, {self.first}"

    @computed_field
    @property
    def initials(self) -> str:
        """Returns just the initials."""
        cleaned = re.sub(r'[\(\[].*?[\)\]]', '', self.full)
        initials = re.findall(r'([^\W_])\w*', cleaned, re.IGNORECASE | re.UNICODE)
        return ''.join(initials).upper()

    @computed_field
    @property
    def mentionable(self) -> str:
        """Returns a mentionable version of the familiar name."""
        return self.familiar[:-1].replace(' ', '').lower()

    def possessive(self, method: Literal["full", "first", "last", "abbreviated", "sorted", "initials"] = "full") -> str:
        """Returns full name with with trailing 's or ' if name ends in s."""
        name = getattr(self, method)
        return f"{name}'" if name.endswith("s") else f"{name}'s"
