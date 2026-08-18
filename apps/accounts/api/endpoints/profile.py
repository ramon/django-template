from ninja import Router

from apps.accounts.api.schemas import UserInfoOut
from apps.accounts.presenters import ProfilePresenter

router = Router(tags=["profile"])


@router.get("/me", response=UserInfoOut, description="Get current user profile")
def profile_me(request):
    return ProfilePresenter(request.user.profile)
