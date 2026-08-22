from django.db import models
from django.utils.translation import gettext_lazy


class DocumentType(models.TextChoices):
    CPF = "cpf", gettext_lazy("CPF")
    SSN = "ssn", gettext_lazy("SSN")
    PASSPORT = "passport", gettext_lazy("passport")
