from ninja import Router

from .endpoints.profile import router as profile_router

router = Router()
router.add_router("/profile/", profile_router)