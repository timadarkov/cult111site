
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1
from app.core.config import settings

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter


is_prod = settings.environment == "production"

app = FastAPI(
    debug=not is_prod,
    docs_url=None if is_prod else "/api/docs",
    redoc_url=None,
    openapi_url=None if is_prod else "/api/openapi.json",
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


origins = settings.host_url


app.include_router(api_v1, prefix="/api/v1")
