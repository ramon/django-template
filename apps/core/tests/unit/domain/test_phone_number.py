import pytest
from apps.core.domain.value_objects.phone_number import PhoneNumber
from pydantic import ValidationError


@pytest.mark.parametrize(
    "phone_input, expected_format",
    [
        ("+5511987654321", "+55 11 98765-4321"),
        ("+14435551234", "+1 443-555-1234"),
        ("+81312345678", "+81 3-1234-5678"),
    ]
)
def test_international_format(phone_input, expected_format):
    """
    Test that the international format method correctly formats phone numbers.
    """
    phone_number = PhoneNumber(root=phone_input)
    assert phone_number.international == expected_format


@pytest.mark.parametrize(
    "phone_input, expected_format",
    [
        ("+5511987654321", "(11) 98765-4321"),
        ("+14435551234", "(443) 555-1234"),
    ]
)
def test_national_format(phone_input, expected_format):
    """
    Test that the national format method correctly formats phone numbers.
    """
    phone_number = PhoneNumber(root=phone_input)
    assert phone_number.national == expected_format


@pytest.mark.parametrize(
    "phone_input, expected_format",
    [
        ("+5511987654321", "+5511987654321"),
        ("+14435551234", "+14435551234"),
    ]
)
def test_e164_format(phone_input, expected_format):
    """
    Test that the E164 format method correctly formats phone numbers.
    """
    phone_number = PhoneNumber(root=phone_input)
    assert phone_number.e164 == expected_format


@pytest.mark.parametrize(
    "phone_input, expected_country_code",
    [
        ("+5511987654321", 55),
        ("+14435551234", 1),
        ("+81312345678", 81),
    ]
)
def test_country_code(phone_input, expected_country_code):
    """
    Test that the country_code method correctly extracts the country code.
    """
    phone_number = PhoneNumber(root=phone_input)
    assert phone_number.country_code == expected_country_code


def test_invalid_phone_number():
    """
    Test that an invalid phone number raises a pydantic.ValidationError.
    """
    with pytest.raises(ValidationError):
        PhoneNumber(root="invalid_phone")
