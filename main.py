
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1
from app.core.config import settings


is_prod = settings.ENVIRONMENT == "production"

app = FastAPI(
    docs_url=None if is_prod else "/api/docs",
    redoc_url=None,
    openapi_url=None if is_prod else "/api/openapi.json",
)


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


origins = settings.host_url

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_v1, prefix="/api/v1")
