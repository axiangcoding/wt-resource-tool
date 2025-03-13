from pydantic import BaseModel


class PlayerTitleDesc(BaseModel):
    id: str
    english: str
    # french: str
    # italian: str
    # german: str
    # spanish: str
    russian: str
    # polish: str
    # czech: str
    # turkish: str
    chinese: str
    # japanese: str
    # portuguese: str
    # ukrainian: str
    # serbian: str
    # hungarian: str
    # korean: str
    # belarusian: str
    # romanian: str
    # vietnamese: str
    # t_chinese: str
    # h_chinese: str
    comments: str
    max_chars: str


class PlayerTitleStorage(BaseModel):
    titles_map: dict[str, PlayerTitleDesc]
    game_version: str
