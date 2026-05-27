from apps.core.models import PersonNameMixin, PhoneNumberMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import pgettext_lazy


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, PersonNameMixin, PhoneNumberMixin):
    """
    Represents a user within the system with authentication and contact details.

    This class extends various mixins and provides a custom user model implementation.
    It includes fields for email, active status, and staff status. The class uses a
    custom manager, `UserManager`, for user-related operations and defines `email`
    as the unique username field. The required fields for creating a user are
    `first_name`, `last_name`, and `phone_number`.

    Attributes:
        email (str): The unique email address of the user, used as the username
            field for authentication.
        is_active (bool): Indicates whether the user's account is active.
        is_staff (bool): Indicates whether the user has administrative privileges.
    """
    email: str = models.EmailField()
    is_active: bool = models.BooleanField(default=True)
    is_staff: bool = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    class Meta:
        verbose_name = pgettext_lazy('model', 'user')
        verbose_name_plural = pgettext_lazy('model', 'users')
        indexes = [
            models.UniqueConstraint(fields=['email']),
        ]