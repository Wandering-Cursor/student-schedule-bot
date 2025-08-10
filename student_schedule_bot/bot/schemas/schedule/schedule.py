import datetime

import pydantic

from bot.schemas.base import Schema
from student_schedule_bot.bot.schemas.schedule.base import NavigatableObject, WithTimestamps


class ScheduleFilters(Schema):
    date__gte: datetime.datetime | None = None
    date__lte: datetime.datetime | None = None
    for_date: datetime.datetime | None = None

    page: int = pydantic.Field(
        le=1,
    )


class Schedule(NavigatableObject, WithTimestamps):
    group_schedules: list[NavigatableObject]

    for_date: datetime.date

    photo_schedule: pydantic.HttpUrl | None = None


class ScheduleResponse(Schema):
    count: int

    next: pydantic.HttpUrl | None
    previous: pydantic.HttpUrl | None

    results: list[Schedule]
