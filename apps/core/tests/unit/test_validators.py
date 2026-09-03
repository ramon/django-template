import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from apps.core.validators import FileSizeValidator


def test_call_accepts_a_file_within_the_limit():
    validator = FileSizeValidator(max_file_size=10)

    validator(ContentFile(b"12345"))  # does not raise


def test_call_rejects_a_file_over_the_limit():
    validator = FileSizeValidator(max_file_size=5)

    with pytest.raises(ValidationError):
        validator(ContentFile(b"123456"))


def test_custom_message_and_code_override_the_defaults():
    validator = FileSizeValidator(max_file_size=5, message="too big", code="too-big")

    assert validator.message == "too big"
    assert validator.code == "too-big"


def test_eq_compares_by_max_file_size_message_and_code():
    assert FileSizeValidator(max_file_size=5) == FileSizeValidator(max_file_size=5)
    assert FileSizeValidator(max_file_size=5) != FileSizeValidator(max_file_size=6)
    assert FileSizeValidator(max_file_size=5) != object()
