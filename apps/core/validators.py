from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.files import File


class FileSizeValidator(BaseValidator):
    message = gettext_lazy("File size must be less than %sMB")
    code = "max_file_size"

    def __init__(self,
                 max_file_size: int = 5 * 1024 * 1024,
                 message: str | None = None,
                 code: str | None = None, ):
        self.max_file_size = max_file_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value: "File"):
        if value.size > self.max_file_size:
            raise ValidationError(
                self.message % str(self.max_file_size / 1024),
                code=self.code,
                params={
                    "max_file_size": self.max_file_size,
                    "value": value,
                },
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.max_file_size == other.max_file_size
            and self.message == other.message
            and self.code == other.code
        )