from typing import Literal

from pydantic import BaseModel

type Country = Literal[
    "country_usa",
    "country_germany",
    "country_ussr",
    "country_britain",
    "country_japan",
    "country_france",
    "country_italy",
    "country_china",
    "country_sweden",
    "country_israel",
    "unknown",
]


class NameI18N(BaseModel):
    english: str
    french: str
    italian: str
    german: str
    spanish: str
    russian: str
    # polish: str
    # czech: str
    # turkish: str
    chinese: str
    japanese: str
    # portuguese: str
    # ukrainian: str
    # serbian: str
    # hungarian: str
    # korean: str
    # belarusian: str
    # romanian: str
    # vietnamese: str
    t_chinese: str
    h_chinese: str
