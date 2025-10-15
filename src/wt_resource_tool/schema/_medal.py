from typing import Literal

from deprecated import deprecated
from pydantic import BaseModel

from wt_resource_tool.schema._common import Country, NameI18N

type ImageType = Literal["normal", "big", "ribbon"]


class PlayerMedalDesc(BaseModel):
    medal_id: str
    country: Country
    name_i18n: NameI18N
    game_version: str

    @deprecated(reason="use get_image_cdn_url instead")
    def get_image_url(
        self,
        mode: ImageType = "normal",
    ) -> str:
        return self.get_image_cdn_url(mode)

    def get_image_cdn_url(
        self,
        mode: ImageType = "normal",
    ) -> str:
        """Get the image CDN URL for the medal.

        CDN is loaded from jsdelivr, which is a free CDN for GitHub repositories.
        """
        prefix = (
            "https://cdn.jsdelivr.net/gh/gszabi99/War-Thunder-Datamine@refs/heads/master/atlases.vromfs.bin_u/medals"
        )
        if mode == "normal":
            return f"{prefix}/{self.medal_id}.png"
        elif mode == "big":
            return f"{prefix}/{self.medal_id}_big.png"
        elif mode == "ribbon":
            return f"{prefix}/{self.medal_id}_ribbon.png"


class ParsedPlayerMedalData(BaseModel):
    medals: list[PlayerMedalDesc]
