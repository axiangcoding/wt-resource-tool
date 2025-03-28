import httpx
from pydantic import BaseModel, Field

from wt_resource_tool._schema import (
    DataSource,
    DataType,
    PlayerMedalDesc,
    PlayerMedalStorage,
    PlayerTitleDesc,
    PlayerTitleStorage,
    Store,
    Vehicle,
    VehicleStorage,
)


class WTResourceTool(BaseModel):
    """
    A tool to get data from War Thunder.

    """

    game_version: str = Field(default="latest")

    # TODO add more source like `local`, `mongodb` etc.
    store: Store = Field(default="memory")

    title_storage: PlayerTitleStorage | None = Field(default=None)
    medal_storage: PlayerMedalStorage | None = Field(default=None)
    vehicle_storage: VehicleStorage | None = Field(default=None)

    async def load_data(
        self,
        datas: list[DataType],
        source: DataSource = "github-jsdelivr",
        store: Store = "memory",
    ):
        if source == "github":
            resource_url_prefix = (
                "https://raw.githubusercontent.com/axiangcoding/wt-resource-tool/refs/heads/main/static"
            )
        elif source == "github-jsdelivr":
            resource_url_prefix = "https://cdn.jsdelivr.net/gh/axiangcoding/wt-resource-tool/static"
        else:
            raise ValueError("Invalid source")
        game_version_str = self.game_version.replace(".", "_")
        if "player_title" in datas:
            resource_url = f"{resource_url_prefix}/{game_version_str}/player_title.json"
            title_data = await self.__get_data_from_remote(resource_url)
            if store == "memory":
                self.title_storage = PlayerTitleStorage.model_validate_json(title_data)
            else:
                raise ValueError("Invalid store")
        if "player_medal" in datas:
            resource_url = f"{resource_url_prefix}/{game_version_str}/player_medal.json"
            medal_data = await self.__get_data_from_remote(resource_url)
            if store == "memory":
                self.medal_storage = PlayerMedalStorage.model_validate_json(medal_data)
            else:
                raise ValueError("Invalid store")
        if "vehicle" in datas:
            resource_url = f"{resource_url_prefix}/{game_version_str}/vehicle.json"
            vehicle_data = await self.__get_data_from_remote(resource_url)
            if store == "memory":
                self.vehicle_storage = VehicleStorage.model_validate_json(vehicle_data)
            else:
                raise ValueError("Invalid store")

    async def get_title(self, title_id: str) -> PlayerTitleDesc:
        if self.title_storage is None:
            raise ValueError("No data loaded")
        return self.title_storage.titles_map[title_id]

    async def get_medal(self, medal_id: str) -> PlayerMedalDesc:
        if self.medal_storage is None:
            raise ValueError("No data loaded")
        return self.medal_storage.medals_map[medal_id]

    async def get_vehicle(self, vehicle_id: str) -> Vehicle:
        if self.vehicle_storage is None:
            raise ValueError("No data loaded")
        return self.vehicle_storage.vehicles_map[vehicle_id]

    async def get_loaded_data_version(self) -> dict[DataType, str | None]:
        return {
            "player_title": self.title_storage.game_version if self.title_storage else None,
            "player_medal": self.medal_storage.game_version if self.medal_storage else None,
        }

    async def __get_data_from_remote(
        self,
        resource_url: str,
    ) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(resource_url)
            resp.raise_for_status()
            storage_text = resp.text
        return storage_text
