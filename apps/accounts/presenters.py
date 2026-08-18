from apps.core.presenters import BasePresenter

from .domain.services import calculate_age
from .models import Profile, User


class UserPresenter(BasePresenter[User]):
    pass


class ProfilePresenter(BasePresenter[Profile]):
    @property
    def name(self) -> str:
        return str(self.obj.user.name.full)

    def first_name(self) -> str:
        return str(self.obj.user.name.first)

    def last_name(self) -> str:
        return str(self.obj.user.name.last)

    def email(self) -> str:
        return str(self.obj.user.email)

    @property
    def age(self) -> int | None:
        return calculate_age(self.obj.birth_date) if self.obj.birth_date else None
