
import logging
from functools import wraps


logger = logging.getLogger(__name__)


def async_log_function_call(func):
    """Логує виклик асинхронної функції."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(
            "Виклик функції: %s",
            func.__name__,
        )

        try:
            result = await func(*args, **kwargs)

            logger.info(
                "Функція %s виконана успішно",
                func.__name__,
            )

            return result

        except Exception:
            logger.exception(
                "Помилка у функції %s",
                func.__name__,
            )
            raise

    return wrapper


def log_user_message(message) -> None:
    """Записує повідомлення користувача в лог."""

    username = message.from_user.username or "без_username"
    text = message.text or "<не текстове повідомлення>"

    logger.info(
        "Користувач: %s | Повідомлення: %s",
        username,
        text,
    )
