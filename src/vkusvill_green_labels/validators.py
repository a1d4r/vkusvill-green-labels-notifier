import datetime
import typing
import zoneinfo

import pydantic


def set_moscow_timezone(v: datetime.datetime) -> datetime.datetime:
    return v.replace(tzinfo=zoneinfo.ZoneInfo("Europe/Moscow"))


MoscowDatetime = typing.Annotated[datetime.datetime, pydantic.AfterValidator(set_moscow_timezone)]
