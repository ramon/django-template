from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.exceptions import ValidationError


def get_errors(e: ValidationError) -> list[str]:
    """
    Extracts error messages from a ValidationError instance.

    This function processes a ValidationError object to extract all associated
    error messages. If a message object contains a `messages` attribute, those messages
    are added directly to the result. Otherwise, the string representation of the error is
    added.

    Args:
        e (ValidationError): The error instance from which to extract messages.

    Returns:
        list[str]: A list of error messages extracted from the ValidationError instance.
    """
    errors = []

    for err in e.error_list:
        if hasattr(err, "messages"):
            errors.extend(err.messages)
        else:
            errors.append(str(err))

    return errors
