import datetime

from apps.accounts.models.mixins import AvatarMixin
from apps.core.models import AbstractBaseModel, AbstractSortableModel
from apps.core.models.mixin import PhoneNumberMixin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import pgettext_lazy

User = get_user_model()


class Gender(AbstractBaseModel, AbstractSortableModel):
    """
    Represents a gender model used for categorizing or identifying gender types.

    This model provides a single attribute to store a gender name. It inherits from
    `AbstractBaseModel` and `AbstractSortableModel`, allowing it to include base
    functionality for sorting and modeling. The class ensures its database-level
    representation has appropriate singular and plural verbose names.

    Attributes:
        name (str): The name of the gender, with a character limit of 20.
    """
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = pgettext_lazy('model', 'gender')
        verbose_name_plural = pgettext_lazy('model', 'genders')


class Profile(AbstractBaseModel,
              PhoneNumberMixin,
              AvatarMixin):
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
    user: User = models.OneToOneField(
        User,
        related_name="profile",
        on_delete=models.CASCADE
    )
    document: str = models.CharField(max_length=11)
    birthday: datetime.date = models.DateField()
    gender: Gender = models.ForeignKey(Gender, on_delete=models.PROTECT)

    class Meta:
        verbose_name = pgettext_lazy('model', 'profile')
        verbose_name_plural = pgettext_lazy('model', 'profiles')
        indexes = [
            models.Index(fields=['document']),
        ]
