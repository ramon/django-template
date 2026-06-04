from typing import Annotated, Union, Self

import phonenumbers

from config.app_settings import get_app_settings
from pydantic import RootModel, Field, model_validator, computed_field
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

E164NumberType = Annotated[
    Union[str, phonenumbers.PhoneNumber], PhoneNumberValidator(
        number_format="E164",
        default_region=get_app_settings().phone_number_region
    )
]

class PhoneNumber(RootModel[str]):
    """
    Represents a phone number with multiple formatting options and information extraction capabilities.

    This class is designed to handle phone numbers with validation and parsing capabilities. It supports
    different formats such as international, national, and E164, and extracts useful components such as
    the country code, area code, and the local phone number. The underlying implementation leverages the
    `phonenumbers` library for parsing.

    Attributes:
        root (E164NumberType): The raw phone number string. Must have a minimum length of 1 and a
            maximum length of 20 characters.
    """
    root: E164NumberType = Field(min_length=1, max_length=20)
    _parsed_number: phonenumbers.PhoneNumber

    @model_validator(mode="after")
    def parse_number(self) -> Self:
        try:
            object.__setattr__(
                self,
                "_parsed_number",
                phonenumbers.parse(str(self.root))
            )
        except phonenumbers.NumberParseException: # pragma: no cover
            raise ValueError("Invalid phone number format.")

        return self

    @computed_field
    @property
    def international(self) -> str | None:
        """Returns the phone number in international format (e.g., +55 11 98765-4321)."""
        if not self._parsed_number:
            return None

        return phonenumbers.format_number(
            self._parsed_number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

    @computed_field
    @property
    def national(self) -> str | None:
        """Returns the phone number in national format (e.g., (11) 98765-4321)."""
        if not self._parsed_number:
            return None

        return phonenumbers.format_number(
            self._parsed_number,
            phonenumbers.PhoneNumberFormat.NATIONAL
        )

    @computed_field
    @property
    def e164(self) -> str:
        """Returns the phone number in E164 format (e.g., +5511987654321)."""
        if not self._parsed_number:
            return str(self.root)

        return phonenumbers.format_number(
            self._parsed_number,
            phonenumbers.PhoneNumberFormat.E164
        )

    @computed_field
    @property
    def country_code(self) -> int | None:
        """Returns the country calling code (e.g., 55 for Brazil)."""
        if not self._parsed_number:
            return None

        return self._parsed_number.country_code