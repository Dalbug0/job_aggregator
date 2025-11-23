from fastapi import Request
from fastapi.responses import JSONResponse

from app.logger import logger


async def http_exception_handler(request: Request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail}
    )


async def generic_exception_handler(request: Request, exc):
    logger.exception("Unexpected error")
    return JSONResponse(
        status_code=500, content={"error": "Internal server error"}
    )
