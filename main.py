
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import validation_exception_handler, integrity_exception_handler
from app.api.v1.router_info import router as info_router
from app.api.v1.router_category import router as categories_router
from app.api.v1.router_brand import router as brands_router
from app.api.v1.router_product import router as products_router
from app.api.v1.router_image import router as images_router
from app.api.v1.router_users import router as users_router
from app.api.v1.router_auth import router as auth_router
from app.core.config import settings
from database import Base, engine


app = FastAPI()

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)

app.add_exception_handler(
    IntegrityError,
    integrity_exception_handler
)

origins = settings.host_url

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(info_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(brands_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


Base.metadata.create_all(bind=engine)
