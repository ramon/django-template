from django.db import models
from django.utils.translation import gettext_lazy


class Gender(models.TextChoices):
    MALE = "male", gettext_lazy("male")
    FEMALE = "female", gettext_lazy("female")
    UNKNOWN = "unknown", gettext_lazy("unknown")
