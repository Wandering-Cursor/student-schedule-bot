import datetime
import re

import pydantic

from bot.schemas.base import Schema
from bot.schemas.schedule.base import NavigatableObject, WithTimestamps


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

    @property
    def photo_schedule_id(self) -> pydantic.UUID4 | None:
        if not self.photo_schedule:
            return None

        match = re.search(r"/([\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12})/", str(self.photo_schedule))
        if match is not None:
            return pydantic.UUID4(match.group(1))  # pyright: ignore[reportCallIssue]

        return None


class ScheduleResponse(Schema):
    count: int

    next: pydantic.HttpUrl | None
    previous: pydantic.HttpUrl | None

    results: list[Schedule]

    @staticmethod
    def get_page_from_url(url: "pydantic.HttpUrl") -> int | None:
        match = re.search(r"page=(\d+)", str(url))
        if match is not None:
            return int(match.group(1))
        return None

    @property
    def next_page_number(self) -> int | None:
        if not self.next:
            return None

        return self.get_page_from_url(self.next)

    @property
    def previous_page_number(self) -> int | None:
        if not self.previous:
            return None

        return self.get_page_from_url(self.previous) or 1


class PhotoItem(WithTimestamps):
    uuid: pydantic.UUID4

    file: pydantic.HttpUrl


class PhotoSchedule(NavigatableObject, WithTimestamps):
    photos: list[PhotoItem]

    name: str | None = None
