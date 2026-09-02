
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.public.router_info import router as info_router
from app.api.v1.public.router_category import router as category_router
from app.api.v1.public.router_brand import router as brand_router
from app.api.v1.public.router_product import router as products_router
from app.api.v1.public.router_product import router as image_router
from app.api.v1.users_public.router_users import router as users_router
from database import Base, engine


app = FastAPI()

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(info_router, prefix="/api/v1/public", tags=["info"])
app.include_router(category_router, prefix="/api/v1/public", tags=["category"])
app.include_router(brand_router, prefix="/api/v1/public", tags=["brand"])
app.include_router(products_router, prefix="/api/v1/public", tags=["product"])
app.include_router(image_router, prefix="/api/v1/public", tags=["image"])

app.include_router(users_router, prefix="/api/v1/users_public", tags=["users"])


Base.metadata.create_all(bind=engine)
