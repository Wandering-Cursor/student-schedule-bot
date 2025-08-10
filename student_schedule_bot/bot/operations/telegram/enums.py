import re
from enum import StrEnum


class ApplicationStates(StrEnum):
    pass


class Commands(StrEnum):
    SHOW_SCHEDULE = "show_schedule"
    SHOW_MAIN_MENU = "show_main_menu"

    @property
    def as_command(self) -> str:
        return self.value.replace("/", "")

    @property
    def as_regex(self) -> str:
        pattern = re.sub(r"\{[^}]+\}", ".*", self.as_command)
        return f"^{pattern}$"
