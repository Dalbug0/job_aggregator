from fastapi import Request
from fastapi.responses import JSONResponse

from app.logger import logger


class TelegramUserAlreadyExists(Exception):
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        super().__init__(f"User with telegram_id {telegram_id} already exists")


class TelegramUserNotFound(Exception):
    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id
        super().__init__(f"Telegram user with telegram_id {telegram_id} not found")


async def http_exception_handler(request: Request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.detail}
    )


async def telegram_user_exception_handler(request, exc: Exception):
    """Обработчик исключений Telegram пользователей"""
    if isinstance(exc, TelegramUserAlreadyExists):
        logger.warning(f"Telegram user registration conflict: {exc.telegram_id}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=409,  # Conflict
            content={"error": str(exc)}
        )
    elif isinstance(exc, TelegramUserNotFound):
        logger.warning(f"Telegram user not found: {exc.telegram_id}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,  # Not Found
            content={"error": str(exc)}
        )
    else:
        # Если это не наше исключение, передать дальше
        raise exc


async def generic_exception_handler(request: Request, exc):
    logger.exception("Unexpected error")
    return JSONResponse(
        status_code=500, content={"error": "Internal server error"}
    )
