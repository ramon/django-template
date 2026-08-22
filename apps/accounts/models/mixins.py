from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy
from django_countries.fields import CountryField
from pydantic import ValidationError as PydanticValidationError

from apps.accounts.domain import Document
from apps.accounts.models.choices import DocumentType
from apps.core.validators import FileSizeValidator


class AvatarMixin(models.Model):
    avatar = models.ImageField(
        gettext_lazy("avatar"),
        upload_to="avatars/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            FileSizeValidator(max_file_size=5 * 1024 * 1024),
        ],
    )

    def avatar_url(self) -> str:
        return self.avatar.url if self.avatar else ""

    class Meta:
        abstract = True


class DocumentMixin(models.Model):
    """
    Mixin providing an official identity document, typed by the person's nationality.

    `nationality` is optional -- a Profile can exist without one. Once set, it
    requires a matching, validated `document`: CPF for Brazil, SSN for the US, and
    an unvalidated passport number for every other nationality (not yet supported
    at the format level). `document_type` is derived from `nationality`, never set
    directly by the caller.

    A CPF made of a single repeated digit (e.g. `111.111.111-11`) is only accepted
    while `settings.DEBUG` is `True` -- it's a common throwaway value in local
    testing, but was never actually issued, so production keeps rejecting it.

    Attributes:
        nationality: The country that issued the document.
        document_type: The kind of document stored in `document`.
        document: The document number, normalized (no punctuation) and, for a
            supported nationality, checksum-validated.
    """

    nationality = CountryField(gettext_lazy("nationality"), blank=True, null=True)
    document_type = models.CharField(
        gettext_lazy("document type"),
        max_length=10,
        choices=DocumentType.choices,
        blank=True,
    )
    document = models.CharField(
        gettext_lazy("document"), max_length=20, null=True, blank=True, unique=True
    )

    class Meta:
        abstract = True

    def clean(self) -> None:
        super().clean()

        if not self.nationality:
            return

        if not self.document:
            raise ValidationError(
                {"document": gettext_lazy("This nationality requires a document number.")}
            )

        try:
            parsed = Document(
                nationality=str(self.nationality),
                value=self.document,
                allow_repeated_digits=settings.DEBUG,
            )
        except PydanticValidationError as exc:
            raise ValidationError(
                {"document": [str(error["msg"]) for error in exc.errors()]}
            ) from exc

        self.document = parsed.value
        self.document_type = parsed.document_type
