import datetime

from PIL.SpiderImagePlugin import TYPE_CHECKING
from apps.accounts.models.mixins import AvatarMixin
from apps.core.models import AbstractBaseModel, AbstractSortableModel
from apps.core.models.mixins import PhoneNumberMixin
from django.conf import settings
from django.db import models
from django.utils.translation import pgettext_lazy

if TYPE_CHECKING:
    from apps.accounts.models.user import User
    from apps.accounts.models.gender import Gender

class ProfileManager(models.Manager):
    def get_queryset(self):
        return (super().get_queryset()
                .select_related('user', 'gender'))


class Profile(AvatarMixin,
              PhoneNumberMixin,
              AbstractBaseModel):
    """
    Represents a user's profile, including personal details and associated data.

    The Profile class is designed to store and manage additional information about
    a user that extends beyond the basic User fields. It includes attributes such
    as the user's document ID, date of birth, gender, and more. This model is
    associated with a single User instance and implements mixins for additional
    functionality.

    Attributes:
        user (User): Defines a one-to-one relationship with the User model,
            ensuring each Profile is associated with a unique User instance.
        document (str): Stores an 11-character string representing the user's
            document ID.
        birthday (datetime.date): Date of birth of the user.
        gender (Gender): Foreign key linking the user's profile with a Gender
            instance, protected against deletion of associated Gender entries.
    """
    user: "User" = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE
    )
    document: str = models.CharField(max_length=11, null=True, blank=True, unique=True)
    birth_date: datetime.date = models.DateField(blank=True, null=True)
    gender: "Gender" = models.ForeignKey('accounts.Gender', blank=True, null=True, on_delete=models.PROTECT)

    objects = ProfileManager()

    class Meta:
        verbose_name = pgettext_lazy('model', 'profile')
        verbose_name_plural = pgettext_lazy('model', 'profiles')
        indexes = [
            models.Index(fields=['document'], name='idx_profile_document'),
        ]

    def __str__(self):
        return self.user.name.full