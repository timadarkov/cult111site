from fastapi import Request
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError
):
    error = exc.errors()[0]

    field = error["loc"][-1]
    error_type = error["type"]

    if field == "password" and error_type == "string_too_short":
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Password must be at least 8 characters"
            }
        )
    elif field == "password" and error_type == "string_too_long":
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Password must be no more than 24 characters"
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid data"
        }
    )


async def integrity_exception_handler(
    _request: Request,
    exc: IntegrityError
):
    if isinstance(exc.orig, UniqueViolation):
        return JSONResponse(
            status_code=409,
            content={
                "detail": "Username already exists"
            }
        )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error"
        }
    )
