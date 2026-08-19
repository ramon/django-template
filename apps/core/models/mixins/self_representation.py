from django.db import models
from django.utils.translation import gettext_lazy


class SelfRepresentationMixin(models.Model):
    """
    Mixin for how a person chooses to be identified, beyond legal/registration data.

    All fields are optional free text: they capture self-reported identity rather
    than a fixed valueset, since gender identity and pronouns aren't enumerable the
    way a simple field like `apps.core.models.Gender` is.

    Attributes:
        social_name: The name the person goes by, when different from their legal
            name.
        gender_identity: How the person identifies their gender, in their own words.
        pronouns: The pronouns the person uses.
    """

    social_name = models.CharField(
        gettext_lazy("social name"), max_length=255, null=True, blank=True
    )
    gender_identity = models.CharField(
        gettext_lazy("gender identity"), max_length=255, null=True, blank=True
    )
    pronouns = models.CharField(gettext_lazy("pronouns"), max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
