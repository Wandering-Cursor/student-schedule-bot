from collections.abc import Callable
from typing import Annotated

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


def convert_string_to_list(v: str | list) -> Callable[..., list[str]]:
    if not v:
        return []
    if isinstance(v, list):
        return v
    return [item.strip() for item in v.split(",")]


StringListValidator = Annotated[
    list[str] | str,
    pydantic.BeforeValidator(convert_string_to_list),
]


class Config(BaseSettings):
    DEBUG: bool = False
    SECRET_KEY: str = "SecretToken-YUot2-hEjkK1uV3sjUZ3Pg"
    ALLOWED_HOSTS: StringListValidator = ["*"]
    TRUSTED_HOSTS: StringListValidator = ["*"]

    DATABASE_CONNECTION: pydantic.AnyUrl = "sqlite:///db.sqlite3"

    TIMEZONE: str = "UTC"
    LANGUAGE_CODE: str = "en-us"

    SCHEDULE_URL: pydantic.HttpUrl = "http://docker.host:8000/api/schedule"

    model_config = SettingsConfigDict(
        env_file=(
            ".env",
            "/run/secrets/env_file",
        ),
        extra="ignore",
    )


config = Config()
