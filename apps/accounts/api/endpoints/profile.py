from apps.accounts.api.schemas import ProfileOut
from apps.accounts.presenters import ProfilePresenter
from ninja import Router

router = Router(tags=['profile'])

@router.get('/me', response=ProfileOut, description='Get current user profile')
def profile_me(request):
    return ProfilePresenter(request.user.profile)
