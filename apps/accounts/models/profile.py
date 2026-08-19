from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy, pgettext_lazy

from apps.accounts.models.mixins import AvatarMixin
from apps.core.models import BaseModel, Gender
from apps.core.models.mixins import PhoneNumberMixin, SelfRepresentationMixin


class ProfileManager(models.Manager["Profile"]):
    def get_queryset(self) -> models.QuerySet[Profile]:
        return super().get_queryset().select_related("user")


class Profile(AvatarMixin, PhoneNumberMixin, SelfRepresentationMixin, BaseModel):
    """
    Represents a user's profile, including personal details and associated data.

    The Profile class is designed to store and manage additional information about
    a user that extends beyond the basic User fields. It includes attributes such
    as the user's document ID, date of birth, gender, and more. This model is
    associated with a single User instance and implements mixins for additional
    functionality.

    Attributes:
        user: Defines a one-to-one relationship with the User model, ensuring
            each Profile is associated with a unique User instance.
        document: Stores an 11-character string representing the user's
            document ID.
        birth_date: Date of birth of the user.
        gender: The person's gender, from a fixed valueset. Defaults to unknown
            rather than requiring a value up front.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=gettext_lazy("user"),
        related_name="profile",
        on_delete=models.CASCADE,
    )
    document = models.CharField(
        gettext_lazy("document"), max_length=11, null=True, blank=True, unique=True
    )
    birth_date = models.DateField(gettext_lazy("birth date"), blank=True, null=True)
    gender = models.CharField(
        gettext_lazy("gender"),
        max_length=10,
        choices=Gender.choices,
        default=Gender.UNKNOWN,
        blank=True,
    )

    objects = ProfileManager()

    class Meta:
        verbose_name = pgettext_lazy("model", "profile")
        verbose_name_plural = pgettext_lazy("model", "profiles")
        indexes = [
            models.Index(fields=["document"], name="idx_profile_document"),
        ]

    @property
    def email(self) -> str:
        """
        Implementa o contrato do AvatarMixin, que precisa do e-mail para o gravatar.

        Sem isto, avatar_url() estourava NotImplementedError sempre que o perfil
        nao tinha imagem enviada -- ou seja, o fallback nunca chegava a rodar.
        """
        return str(self.user.email)

    def __str__(self) -> str:
        return str(self.user.name.full)
