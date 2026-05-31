from typing import TYPE_CHECKING

from apps.core.presenters import BasePresenter
from django.contrib.auth import get_user_model
from .domain.services import calculate_age

if TYPE_CHECKING:
    from .models import Profile

User = get_user_model()


class UserPresenter(BasePresenter[User]):
    pass


class ProfilePresenter(BasePresenter["Profile"]):
    @property
    def name(self) -> str:
        return self.user.name.full

    @property
    def age(self) -> int | None:
        return calculate_age(self.birth_date) if self.birth_date else None
