from typing import Literal

from student_schedule_bot.logger import main_logger


class LoggedHTTPError(Exception):
    STATUS_CODE = 500
    DEFAULT_MESSAGE = {
        "msg": "Unknown error occurred",
    }

    def __init__(
        self,
        message: dict | str | None = None,
        log_message: dict | str | None = None,
        level: Literal["warning", "error", "exception"] = "error",
    ) -> None:
        self.status_code = self.STATUS_CODE

        if isinstance(message, str):
            message = {
                "msg": message,
            }

        self.message = message or self.DEFAULT_MESSAGE
        self.log_message = log_message or self.message

        match level:
            case "warning":
                main_logger.warning(self.log_message)
            case "error":
                main_logger.error(self.log_message)
            case "exception":
                main_logger.exception(self.log_message)
            case _:
                raise ValueError(f"Invalid log level: {level}")

    def __str__(self) -> str:
        return f"HTTP Error {self.status_code}: {self.message}"

    def __repr__(self) -> str:
        return (
            f"LoggedHTTPError(status_code={self.status_code}, message={self.message}, log_message={self.log_message})"
        )


class AuthenticationError(LoggedHTTPError):
    DEFAULT_MESSAGE = {
        "msg": "Authentication failed",
    }
    STATUS_CODE = 401


class AuthorizationError(LoggedHTTPError):
    DEFAULT_MESSAGE = {
        "msg": "Authorization failed",
    }
    STATUS_CODE = 403


class InvalidRequestError(LoggedHTTPError):
    DEFAULT_MESSAGE = {
        "msg": "Invalid request",
    }
    STATUS_CODE = 400


class NotFoundError(LoggedHTTPError):
    DEFAULT_MESSAGE = {
        "msg": "Resource not found",
    }
    STATUS_CODE = 404
