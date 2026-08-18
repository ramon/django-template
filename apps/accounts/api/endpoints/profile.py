from typing import TYPE_CHECKING, cast

from django.http import HttpRequest
from ninja import Router

from apps.accounts.api.schemas import UserInfoOut
from apps.accounts.presenters import ProfilePresenter

if TYPE_CHECKING:
    from apps.accounts.models import User

router = Router(tags=["profile"])


@router.get("/me", response=UserInfoOut, description="Get current user profile")
def profile_me(request: HttpRequest) -> ProfilePresenter:
    # a NinjaAPI exige django_auth globalmente, entao o usuario nunca e' anonimo aqui
    user = cast("User", request.user)
    return ProfilePresenter(user.profile)
