
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import logging

from app.api.v1.router import router as api_v1
from app.core.config import settings


from app.core.middleware import log_requests

from app.core.rate_limit import limiter
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


is_prod = settings.environment == "production"


app = FastAPI(
    debug=not is_prod,
    docs_url=None if is_prod else "/api/docs",
    redoc_url=None,
    openapi_url=None if is_prod else "/api/openapi.json",
)


app.middleware("http")(log_requests)

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

app.include_router(api_v1, prefix="/api/v1")


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}


origins = settings.host_url

logger.info("Application started")
