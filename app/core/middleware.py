import logging
from time import perf_counter

from fastapi import Request


logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next):
    start = perf_counter()

    response = await call_next(request)

    duration_ms = (perf_counter() - start) * 1000

    logger.info(
        "%s %s -> %s | %.0f ms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response
