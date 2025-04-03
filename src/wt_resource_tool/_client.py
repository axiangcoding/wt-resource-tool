import asyncio
import time
from tracemalloc import start
from typing import Literal

import httpx
from loguru import logger
from pydantic import BaseModel, Field

from wt_resource_tool.parser import player_medal_parser, player_title_parser, vehicle_data_parser
from wt_resource_tool.schema._wt_schema import (
    PlayerMedalDesc,
    PlayerMedalStorage,
    PlayerTitleDesc,
    PlayerTitleStorage,
    Vehicle,
    VehicleStorage,
)

type DataType = Literal["player_title", "player_medal", "vehicle"]
type DataSource = Literal["github", "github-jsdelivr"] | str


class WTResourceTool(BaseModel):
    """
    A tool to parse and get data about War Thunder.

    """

    title_storage: PlayerTitleStorage | None = Field(default=None)
    medal_storage: PlayerMedalStorage | None = Field(default=None)
    vehicle_storage: VehicleStorage | None = Field(default=None)

    async def load_parsed_data(
        self,
        data_types: list[DataType],
        game_version: str = "latest",
        source: DataSource = "github-jsdelivr",
    ):
        """
        Load pre-parsed data from remote.
        The data is stored in the static folder of the repository.

        Args:
            data_types (list[DataType]): The data types to load.
            game_version (str): The game version to load. Default is "latest".
            source (DataSource): The source of the data. Default is "github-jsdelivr". It can be "github", "github-jsdelivr" or a custom url.
        """
        start_time = time.time()
        if source == "github":
            resource_url_prefix = (
                "https://raw.githubusercontent.com/axiangcoding/wt-resource-tool/refs/heads/main/static"
            )
        elif source == "github-jsdelivr":
            resource_url_prefix = "https://cdn.jsdelivr.net/gh/axiangcoding/wt-resource-tool/static"
        else:
            if not source.startswith("https:// "):
                raise ValueError("Custom source must be a valid safe url")
            resource_url_prefix = source
        game_version_folder_str = game_version.replace(".", "_")

        if "player_title" in data_types:
            resource_url = f"{resource_url_prefix}/{game_version_folder_str}/player_title.json"
            logger.debug("Loading player title data from {}", resource_url)
            title_data = await self.__get_data_from_remote(resource_url)
            self.title_storage = PlayerTitleStorage.model_validate_json(title_data)

        if "player_medal" in data_types:
            resource_url = f"{resource_url_prefix}/{game_version_folder_str}/player_medal.json"
            logger.debug("Loading player medal data from {}", resource_url)
            medal_data = await self.__get_data_from_remote(resource_url)

            self.medal_storage = PlayerMedalStorage.model_validate_json(medal_data)

        if "vehicle" in data_types:
            resource_url = f"{resource_url_prefix}/{game_version_folder_str}/vehicle.json"
            logger.debug("Loading vehicle data from {}", resource_url)
            vehicle_data = await self.__get_data_from_remote(resource_url)
            self.vehicle_storage = VehicleStorage.model_validate_json(vehicle_data)

        end_time = time.time()
        logger.debug(
            "Loaded data in {} seconds",
            round(end_time - start_time, 2),
        )

    async def parse_and_load_data(
        self,
        data_types: list[DataType],
        local_repo_path: str,
        git_pull_when_empty: bool = False,
    ):
        """
        Parse and load data from local repo.

        This action may take a long time if repo not exist. Because it needs to clone the repo first.

        Args:
            data_types (list[DataType]): The data types to load.
            local_repo_path (str): The local repo path.
            git_pull_when_empty (bool): Whether to pull the repo when it is empty. Default is False.
        """
        # TODO check if the repo is empty and pull it if it is empty
        start_time = time.time()
        if "player_title" in data_types:
            logger.debug("Parsing player title data from {}", local_repo_path)
            ms = await asyncio.to_thread(lambda: player_medal_parser.parse_player_medal(local_repo_path))
            self.medal_storage = ms
        if "player_medal" in data_types:
            logger.debug("Parsing player medal data from {}", local_repo_path)
            ts = await asyncio.to_thread(lambda: player_title_parser.parse_player_title(local_repo_path))
            self.title_storage = ts
        if "vehicle" in data_types:
            logger.debug("Parsing vehicle data from {}", local_repo_path)
            vs = await asyncio.to_thread(lambda: vehicle_data_parser.parse_vehicle_data(local_repo_path))
            self.vehicle_storage = vs
        end_time = time.time()
        logger.debug(
            "Parsed data in {} seconds",
            round(end_time - start_time, 2),
        )

    async def get_loaded_data_version(self) -> dict[DataType, str | None]:
        return {
            "player_title": self.title_storage.game_version if self.title_storage else None,
            "player_medal": self.medal_storage.game_version if self.medal_storage else None,
            "vehicle": self.vehicle_storage.game_version if self.vehicle_storage else None,
        }

    async def get_title(self, title_id: str) -> PlayerTitleDesc:
        """
        Get title data by id.

        """
        if self.title_storage is None:
            raise ValueError("No data loaded")
        return self.title_storage.titles_map[title_id]

    async def get_medal(self, medal_id: str) -> PlayerMedalDesc:
        """
        Get medal data by id.

        """
        if self.medal_storage is None:
            raise ValueError("No data loaded")
        return self.medal_storage.medals_map[medal_id]

    async def get_vehicle(self, vehicle_id: str) -> Vehicle:
        """
        Get vehicle data by id.

        """
        if self.vehicle_storage is None:
            raise ValueError("No data loaded")
        return self.vehicle_storage.vehicles_map[vehicle_id]

    async def __get_data_from_remote(
        self,
        resource_url: str,
    ) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(resource_url)
            resp.raise_for_status()
            storage_text = resp.text
        return storage_text
