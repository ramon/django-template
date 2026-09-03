from typing import ClassVar

import pytest
from django.core.exceptions import ValidationError

from apps.core.services import get_errors


@pytest.mark.parametrize(
    "error_input, expected_output",
    [
        (ValidationError("This is an error message."), ["This is an error message."]),
        (
            ValidationError(
                [
                    "Error one.",
                    ValidationError("Error two."),
                ]
            ),
            ["Error one.", "Error two."],
        ),
        (
            ValidationError(
                [
                    ValidationError("Nested error."),
                ]
            ),
            ["Nested error."],
        ),
        (
            ValidationError(
                [
                    ValidationError({"field1": ["Error for field1", "Another error"]}),
                ]
            ),
            ["Error for field1", "Another error"],
        ),
    ],
)
def test_get_errors_handles_validation_error(error_input, expected_output):
    """
    Test get_errors function with various ValidationError inputs.
    """
    result = get_errors(error_input)
    assert result == expected_output


def test_get_errors_handles_empty_error_list():
    """
    Test get_errors function with an empty ValidationError.
    """
    error = ValidationError([])
    result = get_errors(error)
    assert result == []


def test_get_errors_falls_back_to_str_without_a_messages_attribute():
    """
    Test get_errors function with an error_list item that has no `messages`
    attribute -- every real `ValidationError` has one, but `get_errors` only
    duck-types on `error_list`, so any object shaped like it works.
    """

    class _FakeValidationError:
        error_list: ClassVar = ["a plain string error"]

    result = get_errors(_FakeValidationError())  # type: ignore[arg-type]
    assert result == ["a plain string error"]
