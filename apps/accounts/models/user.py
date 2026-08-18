from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy

from apps.core.models import BaseModel, PersonNameMixin, PhoneNumberMixin


class UserManager(BaseUserManager["User"]):
    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
        if not email:
            raise ValueError("The Email must be set")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()

        from apps.accounts.models import Profile

        Profile.objects.create(user=user)

        return user

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: Any
    ) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(PermissionsMixin, PersonNameMixin, PhoneNumberMixin, BaseModel, AbstractBaseUser):
    """
    Represents a user within the system with authentication and contact details.

    This class extends various mixins and provides a custom user model implementation.
    It includes fields for email, active status, and staff status. The class uses a
    custom manager, `UserManager`, for user-related operations and defines `email`
    as the unique username field. The required fields for creating a user are
    `first_name`, `last_name`, and `phone_number`.

    Attributes:
        email: The unique email address of the user, used as the username field
            for authentication.
        is_active: Indicates whether the user's account is active.
        is_staff: Indicates whether the user has administrative privileges.
    """

    email = models.EmailField(gettext_lazy("email"), unique=True)
    is_active = models.BooleanField(gettext_lazy("is active"), default=True)
    is_staff = models.BooleanField(gettext_lazy("is staff"), default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    class Meta:
        verbose_name = pgettext_lazy("model", "user")
        verbose_name_plural = pgettext_lazy("model", "users")
        indexes = [
            models.Index(fields=["first_name", "last_name"], name="idx_user_full_name"),
            models.Index(fields=["phone_number"], name="idx_user_phone_number"),
        ]

    def __str__(self) -> str:
        return str(self.name.full)
