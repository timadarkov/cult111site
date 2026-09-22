from fastapi import APIRouter, Depends

from app.dependency import get_current_user, get_current_admin

from app.api.v1.auth.auth import router as auth_router

from app.api.v1.public.product import router as public_products_router
from app.api.v1.public.category import router as public_categories_router
from app.api.v1.public.info import router as public_info_router
from app.api.v1.public.image import router as public_images_router
from app.api.v1.public.users import router as public_users_router
from app.api.v1.public.brand import router as public_brands_router


from app.api.v1.admin.brand import router as admin_brands_router
from app.api.v1.admin.users import router as admin_users_router
from app.api.v1.admin.info import router as admin_info_router
from app.api.v1.admin.category import router as admin_categories_router
from app.api.v1.admin.product import router as admin_products_router
from app.api.v1.admin.image import router as admin_images_router


router = APIRouter(prefix="/api/v1")


router.include_router(
    auth_router,
    prefix="/auth",
)


router.include_router(public_brands_router)
router.include_router(public_products_router)
router.include_router(public_categories_router)
router.include_router(public_info_router)
router.include_router(public_images_router)
router.include_router(public_users_router)


admin_router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_admin)],
)


admin_router.include_router(admin_brands_router)
admin_router.include_router(admin_users_router)
admin_router.include_router(admin_info_router)
admin_router.include_router(admin_categories_router)
admin_router.include_router(admin_products_router)
admin_router.include_router(admin_images_router)
router.include_router(admin_router)
