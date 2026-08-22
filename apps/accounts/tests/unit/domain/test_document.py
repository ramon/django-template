import pytest
from pydantic import ValidationError

from apps.accounts.domain.value_objects.document import Document


@pytest.mark.parametrize(
    "raw_value, expected_value",
    [
        ("529.982.247-25", "52998224725"),
        ("52998224725", "52998224725"),
    ],
)
def test_br_nationality_validates_and_normalizes_cpf(raw_value, expected_value):
    document = Document(nationality="BR", value=raw_value)

    assert document.document_type == "cpf"
    assert document.value == expected_value


def test_br_nationality_rejects_invalid_cpf():
    with pytest.raises(ValidationError):
        Document(nationality="BR", value="123.456.789-00")


@pytest.mark.parametrize(
    "raw_value, expected_value",
    [
        ("123-45-6789", "123456789"),
        ("123456789", "123456789"),
    ],
)
def test_us_nationality_validates_and_normalizes_ssn(raw_value, expected_value):
    document = Document(nationality="US", value=raw_value)

    assert document.document_type == "ssn"
    assert document.value == expected_value


def test_us_nationality_rejects_invalid_ssn():
    with pytest.raises(ValidationError):
        Document(nationality="US", value="000-00-0000")


def test_unsupported_nationality_falls_back_to_passport():
    document = Document(nationality="FR", value="ab 12-cd 34")

    assert document.document_type == "passport"
    assert document.value == "AB12CD34"


def test_unsupported_nationality_only_requires_an_alphanumeric_value():
    with pytest.raises(ValidationError):
        Document(nationality="FR", value=" -- ")
