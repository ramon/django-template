from apps.accounts.api.schemas import ProfileOut
from ninja import Router

router = Router(tags=['profile'])

@router.get('/me', response=ProfileOut, description='Get current user profile')
def profile_me(request):
    return request.user.profile
