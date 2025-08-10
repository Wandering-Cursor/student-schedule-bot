from typing import TYPE_CHECKING

from student_schedule_bot.bot.schemas.schedule.schedule import ScheduleResponse
from student_schedule_bot.config import config
from student_schedule_bot.libs.requests.sender import RequestSender

if TYPE_CHECKING:
    from bot.models.user import User


sender = RequestSender(
    "student_schedule_bot/0.0.0",
    base_url=config.schedule_url,
)


async def get_schedule(
    user: "User",
) -> ScheduleResponse:
    # NOTE: Use user's group for filtering? (Note that it only works for Group's schedule though 🤔)
    # For Future

    pass


async def get_schedule_using_url(
    url: str,
) -> None:
    pass
