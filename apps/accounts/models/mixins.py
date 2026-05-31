from apps.core.validators import FileSizeValidator
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.accounts.services import gravatar_url


class AvatarMixin(models.Model):
    avatar: models.ImageField = models.ImageField(
        upload_to='avatars/',
        blank=True, null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            FileSizeValidator(max_file_size=5 * 1024 * 1024),
        ]
    )

    @property
    def email(self) -> str:
        raise NotImplementedError("Subclasses must implement email method")


    def avatar_url(self) -> str:
        return self.avatar.url if self.avatar else gravatar_url(self.email)


    class Meta:
        abstract = True