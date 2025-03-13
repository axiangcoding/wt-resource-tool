from typing import Literal

import httpx
from pydantic import BaseModel, Field

from wt_resource_tool._schema import PlayerTitleDesc, PlayerTitleStorage

type PlayerTitleSource = Literal["github", "github-jsdelivr", "repo-mirror"]

type Store = Literal["memory"]


class WTPlayerTitleTool(BaseModel):
    """
    A tool to get player title data

    """

    # TODO add more source like `local`, `mongodb` etc.
    store: Store = Field(default="memory")

    memory_storage: PlayerTitleStorage | None = Field(default=None)

    async def load_data(
        self,
        source: PlayerTitleSource = "github",
        source_repo_prefiix: str | None = None,
        store: Store = "memory",
        game_version: str = "latest",
    ):
        game_version_str = game_version.replace(".", "_")
        if source == "github":
            resource_url = f"https://raw.githubusercontent.com/axiangcoding/wt-resource-tool/refs/heads/main/static/{game_version_str}/player_title.json"
        elif source == "github-jsdelivr":
            resource_url = (
                f"https://cdn.jsdelivr.net/gh/axiangcoding/wt-resource-tool/static/{game_version_str}/player_title.json"
            )
        elif source == "repo-mirror":
            if source_repo_prefiix is None:
                raise ValueError("source_repo_prefiix is required")
            resource_url = f"{source_repo_prefiix}/static/{game_version_str}/player_title.json"
        else:
            raise ValueError("Invalid source")
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(resource_url)
            resp.raise_for_status()
            storage_text = resp.text
        if store == "memory":
            self.memory_storage = PlayerTitleStorage.model_validate_json(storage_text)
        else:
            raise ValueError("Invalid store")

    async def get_title(self, title_id: str) -> PlayerTitleDesc:
        if self.memory_storage is None:
            raise ValueError("No data loaded")
        return self.memory_storage.titles_map[title_id]

    async def get_game_version(self) -> str:
        if self.memory_storage is None:
            raise ValueError("No data loaded")
        return self.memory_storage.game_version
