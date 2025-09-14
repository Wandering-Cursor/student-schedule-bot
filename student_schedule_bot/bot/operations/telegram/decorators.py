from typing import TypeVar

from asgiref.sync import sync_to_async
from django.db import close_old_connections

FunctionType = TypeVar("FunctionType")


def handler_decorator() -> FunctionType:
    def decorator(
        func: FunctionType,
    ) -> FunctionType:
        async def wrapper(
            *args,  # noqa: ANN002
            **kwargs,  # noqa: ANN003
        ) -> None:
            await sync_to_async(close_old_connections)()
            return await func(*args, **kwargs)

        return wrapper

    return decorator
