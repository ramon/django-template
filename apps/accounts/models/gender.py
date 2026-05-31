from apps.core.models import AbstractBaseModel, AbstractSortableModel
from django.db import models
from django.utils.translation import pgettext_lazy


class Gender(AbstractSortableModel, AbstractBaseModel):
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