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
                phonenumbers.parse(self.root)
            )
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format.")

        return self

    @computed_field
    @property
    def international(self) -> str:
        """Returns the phone number in international format (e.g., +55 11 98765-4321)."""
        if self._parsed_number:
            return phonenumbers.format_number(
                self._parsed_number,
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        return self.root

    @computed_field
    @property
    def national(self) -> str:
        """Returns the phone number in national format (e.g., (11) 98765-4321)."""
        if self._parsed_number:
            return phonenumbers.format_number(
                self._parsed_number,
                phonenumbers.PhoneNumberFormat.NATIONAL
            )
        return self.root

    @computed_field
    @property
    def e164(self) -> str:
        """Returns the phone number in E164 format (e.g., +5511987654321)."""
        if self._parsed_number:
            return phonenumbers.format_number(
                self._parsed_number,
                phonenumbers.PhoneNumberFormat.E164
            )
        return self.root

    @computed_field
    @property
    def country_code(self) -> int:
        """Returns the country calling code (e.g., 55 for Brazil)."""
        if self._parsed_number:
            return self._parsed_number.country_code
        return 0

    @computed_field
    @property
    def area_code(self) -> int:
        """Returns the area code (DDD) for Brazilian phone numbers (e.g., '11' for São Paulo)."""
        if self._parsed_number:
            national_number = str(self._parsed_number.national_number)
            # Brazilian mobile numbers have 11 digits (2 DDD + 9 digits)
            # Brazilian landline numbers have 10 digits (2 DDD + 8 digits)
            if len(national_number) >= 10:
                return int(national_number[:2])
        return 0

    @computed_field
    @property
    def number_only(self) -> str:
        """Returns the phone number without area code for Brazilian phone numbers."""
        if self._parsed_number:
            national_number = str(self._parsed_number.national_number)
            # Remove the first 2 digits (area code/DDD)
            if len(national_number) >= 10:
                return national_number[2:]
        return self.root