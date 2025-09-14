import re
from enum import StrEnum


class ApplicationStates(StrEnum):
    pass


class Commands(StrEnum):
    SHOW_SCHEDULE = "show_schedule"
    SHOW_MAIN_MENU = "show_main_menu"

    SCHEDULE_PAGE = "schedule_page?page="

    SHOW_ITEM = "show_item?id="

    SHOW_PHOTO_SCHEDULE = "show_photo_schedule?id="

    @property
    def as_command(self) -> str:
        return self.value.replace("/", "")

    @property
    def as_regex(self) -> str:
        pattern = re.sub(r"\{[^}]+\}", ".*", self.as_command.replace("?", r"\?"))

        if self == Commands.SCHEDULE_PAGE:
            pattern = pattern.replace("page=", r"page=\d")
        if self in [Commands.SHOW_ITEM, Commands.SHOW_PHOTO_SCHEDULE]:
            pattern = pattern.replace("id=", r"id=.*")

        return f"^{pattern}$"

    @classmethod
    def schedule_page(cls, page_no: int) -> str:
        return f"{cls.SCHEDULE_PAGE.value}{page_no}"

    @classmethod
    def show_item(cls, item_id: str) -> str:
        return f"{cls.SHOW_ITEM.value}{item_id}"

    @classmethod
    def show_photo_schedule(cls, photo_id: str, item_id: str | None) -> str:
        if not item_id:
            return f"{cls.SHOW_PHOTO_SCHEDULE.value}{photo_id}"

        return f"{cls.SHOW_PHOTO_SCHEDULE.value}{photo_id}?item_id={item_id}"
