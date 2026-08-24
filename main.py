
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.home import router as main_router
from app.api.v1.home import router as category_router
from app.api.v1.home import router as brand_router
from app.api.v1.home import router as products_router
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


# from models import Wallet



app.include_router(main_router, prefix="/api/v1", tags=["main"])
app.include_router(category_router, prefix="/api/v1", tags=["category"])
app.include_router(brand_router, prefix="/api/v1", tags=["brand"])
app.include_router(products_router, prefix="/api/v1", tags=["product"])

Base.metadata.create_all(bind=engine)



