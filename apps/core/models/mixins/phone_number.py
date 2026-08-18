from functools import cached_property

from django.db import models

from apps.core.domain import PhoneNumber


class PhoneNumberMixin(models.Model):
    """
    Mixin providing phone number support for models.

    This mixin allows models to store, retrieve, and manipulate phone numbers.
    It defines a phone number field stored in the E.164 format and provides
    access to the parsed `PhoneNumber` object via a setter and getter property.

    Attributes:
        phone_number (str): A string representing the phone number stored in the
                            database. It is nullable and can be left blank.
    """

    phone_number = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True

    @cached_property
    def _cached_phone(self) -> PhoneNumber | None:  # pragma: no cover
        return PhoneNumber(self.phone_number) if self.phone_number else None

    @property
    def phone(self) -> PhoneNumber | None:
        return self._cached_phone

    @phone.setter
    def phone(self, phone_number: str) -> None:
        parsed = PhoneNumber(phone_number)
        self.phone_number = parsed.e164

        self.__dict__.pop("_cached_phone", None)
