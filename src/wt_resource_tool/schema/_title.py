from pydantic import BaseModel, Field

from wt_resource_tool.schema._common import NameI18N


class PlayerTitleDesc(BaseModel):
    title_id: str
    description_i18n: NameI18N | None = Field(default=None)
    name_i18n: NameI18N
    game_version: str


class ParsedPlayerTitleData(BaseModel):
    titles: list[PlayerTitleDesc]
