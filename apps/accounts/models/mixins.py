from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy

from apps.accounts.services import gravatar_url
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

    @property
    def email(self) -> str:
        raise NotImplementedError("Subclasses must implement email method")

    def avatar_url(self) -> str:
        return self.avatar.url if self.avatar else gravatar_url(self.email)

    class Meta:
        abstract = True
