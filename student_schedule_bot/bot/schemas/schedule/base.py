import datetime

import pydantic

from bot.schemas.base import Schema


class NavigatableObject(Schema):
    url: pydantic.HttpUrl
    uuid: pydantic.UUID4


class WithCreationTime(Schema):
    created_at: datetime.datetime


class WithUpdateTime(Schema):
    updated_at: datetime.datetime


class WithTimestamps(WithCreationTime, WithUpdateTime):
    pass
