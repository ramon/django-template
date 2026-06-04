import pytest
from apps.core.services import get_errors
from django.core.exceptions import ValidationError


@pytest.mark.parametrize(
    "error_input, expected_output",
    [
        (
                ValidationError("This is an error message."),
                ["This is an error message."]
        ),
        (
                ValidationError(
                    [
                        "Error one.",
                        ValidationError("Error two."),
                    ]
                ),
                ["Error one.", "Error two."]
        ),
        (
                ValidationError(
                    [
                        ValidationError("Nested error."),
                    ]
                ),
                ["Nested error."]
        ),
        (
                ValidationError(
                    [
                        ValidationError({"field1": ["Error for field1", "Another error"]}),
                    ]
                ),
                ["Error for field1", "Another error"]
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
