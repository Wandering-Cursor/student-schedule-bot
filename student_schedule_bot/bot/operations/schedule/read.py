from typing import TYPE_CHECKING

from django.core.cache import cache
from libs.requests.sender import HttpxRequestParameters, RequestSender
from libs.requests.status_codes import OK_200

from bot.schemas.schedule.schedule import ScheduleFilters, ScheduleResponse
from student_schedule_bot.config import config

if TYPE_CHECKING:
    from bot.models.user import User


sender = RequestSender(
    "student_schedule_bot/0.0.0",
    base_url=str(config.SCHEDULE_URL),
)


async def get_schedule(
    user: "User",
    filters: "ScheduleFilters | None" = None,
) -> ScheduleResponse:
    # NOTE: Use user's group for filtering? (Note that it only works for Group's schedule though 🤔)
    # For Future
    if not filters:
        filters = ScheduleFilters(page=1)

    cache_key = f"schedule_{user.pk}_{filters.model_dump()}"

    response = cache.get(cache_key, default=None)
    if response:
        return ScheduleResponse.model_validate(response)

    response = await sender.send_async(
        "GET",
        "/schedule/schedule/",
        HttpxRequestParameters(
            params=filters.model_dump(),
        ),
    )

    if response.status_code != OK_200:
        raise RuntimeError(
            {
                "msg": "Failed to get schedule",
                "response": response,
                "response.content": response.content,
                "response.request.url": response.request.url,
            }
        )

    result = ScheduleResponse.model_validate(response.json())

    cache.set(
        cache_key,
        result,
        timeout=60 * 5,
    )

    return result


async def get_schedule_using_url(
    url: str,
) -> None:
    pass
