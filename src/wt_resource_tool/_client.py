import asyncio
import time
from abc import abstractmethod
from typing import Literal

import numpy as np
from loguru import logger
from pandas import DataFrame
from pydantic import BaseModel

from wt_resource_tool.parser import player_medal_parser, player_title_parser, vehicle_data_parser
from wt_resource_tool.schema._wt_schema import (
    ParsedPlayerMedalData,
    ParsedPlayerTitleData,
    ParsedVehicleData,
    PlayerMedalDesc,
    PlayerTitleDesc,
    VehicleDesc,
)

type DataType = Literal["player_title", "player_medal", "vehicle"]


class WTResourceTool(BaseModel):
    """
    A tool to parse and get data about War Thunder.

    """

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
        start_time = time.perf_counter()
        if "player_title" in data_types:
            logger.debug("Parsing player title data from {}", local_repo_path)
            ts = await asyncio.to_thread(lambda: player_title_parser.parse_player_title(local_repo_path))
            await self.save_player_title_data(ts)

        if "player_medal" in data_types:
            logger.debug("Parsing player medal data from {}", local_repo_path)
            ms = await asyncio.to_thread(lambda: player_medal_parser.parse_player_medal(local_repo_path))
            await self.save_player_medal_data(ms)

        if "vehicle" in data_types:
            logger.debug("Parsing vehicle data from {}", local_repo_path)
            vs = await asyncio.to_thread(lambda: vehicle_data_parser.parse_vehicle_data(local_repo_path))
            await self.save_vehicle_data(vs)

        end_time = time.perf_counter()
        logger.info(
            f"Parsed and load data {data_types} in {round(end_time - start_time, 2)} seconds",
        )

    async def get_title(
        self,
        title_id: str,
        game_version: str = "latest",
    ) -> PlayerTitleDesc | None:
        """
        Get title data by id.

        """
        return await self.get_player_title_data(title_id, game_version=game_version)

    async def get_medal(
        self,
        medal_id: str,
        game_version: str = "latest",
    ) -> PlayerMedalDesc | None:
        """
        Get medal data by id.

        """
        return await self.get_player_medal_data(medal_id, game_version=game_version)

    async def get_vehicle(
        self,
        vehicle_id: str,
        game_version: str = "latest",
    ) -> VehicleDesc | None:
        """
        Get vehicle data by id.

        """
        return await self.get_vehicle_data(vehicle_id, game_version=game_version)

    @abstractmethod
    async def save_player_title_data(
        self,
        title_data: ParsedPlayerTitleData,
    ): ...

    @abstractmethod
    async def get_player_title_data(
        self,
        title_id: str,
        game_version: str,
    ) -> PlayerTitleDesc | None: ...

    @abstractmethod
    async def save_player_medal_data(
        self,
        medal_data: ParsedPlayerMedalData,
    ): ...

    @abstractmethod
    async def get_player_medal_data(
        self,
        medal_id: str,
        game_version: str,
    ) -> PlayerMedalDesc | None: ...

    @abstractmethod
    async def save_vehicle_data(
        self,
        vehicle_data: ParsedVehicleData,
    ): ...

    @abstractmethod
    async def get_vehicle_data(
        self,
        vehicle_id: str,
        game_version: str,
    ) -> VehicleDesc | None: ...


class WTResourceToolMemory(WTResourceTool):
    """A tool to parse and get data about War Thunder.

    This class stores the data in memory.
    """

    model_config = {"arbitrary_types_allowed": True}

    player_title_storage: DataFrame | None = None
    """title storage"""

    player_title_latest_version: str | None = None
    """latest version of title storage"""

    player_medal_storage: DataFrame | None = None
    """medal storage"""

    player_medal_latest_version: str | None = None
    """latest version of medal storage"""

    vehicle_storage: DataFrame | None = None
    """vehicle storage"""

    vehicle_latest_version: str | None = None
    """latest version of vehicle storage"""

    async def save_player_title_data(
        self,
        title_data: ParsedPlayerTitleData,
    ):
        data = []
        for title in title_data.titles:
            data.append(title.model_dump())
        self.player_title_storage = DataFrame(data)
        self.player_title_latest_version = title_data.titles[0].game_version

    async def get_player_title_data(
        self,
        title_id: str,
        game_version: str = "latest",
    ) -> PlayerTitleDesc | None:
        if self.player_title_storage is None:
            raise ValueError("Player title data not loaded")
        if game_version == "latest":
            if self.player_title_latest_version is None:
                raise ValueError("Player title version not loaded")
            game_version = self.player_title_latest_version
        title_data = self.player_title_storage[self.player_title_storage["game_version"] == game_version]
        title_data = title_data[title_data["title_id"] == title_id]
        if title_data.empty:
            return None
        return PlayerTitleDesc.model_validate(title_data.iloc[0].to_dict())

    async def save_player_medal_data(self, medal_data: ParsedPlayerMedalData):
        data = []
        for medal in medal_data.medals:
            data.append(medal.model_dump())
        self.player_medal_storage = DataFrame(data)
        self.player_medal_latest_version = medal_data.medals[0].game_version

    async def get_player_medal_data(
        self,
        medal_id: str,
        game_version: str = "latest",
    ) -> PlayerMedalDesc | None:
        if self.player_medal_storage is None:
            raise ValueError("Player medal data not loaded")
        if game_version == "latest":
            if self.player_medal_latest_version is None:
                raise ValueError("Player medal version not loaded")
            game_version = self.player_medal_latest_version
        medal_data = self.player_medal_storage[self.player_medal_storage["game_version"] == game_version]
        medal_data = medal_data[medal_data["medal_id"] == medal_id]
        if medal_data.empty:
            return None
        return PlayerMedalDesc.model_validate(medal_data.iloc[0].to_dict())

    async def save_vehicle_data(self, vehicle_data: ParsedVehicleData):
        data = []
        for vehicle in vehicle_data.vehicles:
            data.append(vehicle.model_dump())
        df = DataFrame(data)
        df = df.replace({np.nan: None})
        self.vehicle_storage = df
        self.vehicle_latest_version = vehicle_data.vehicles[0].game_version

    async def get_vehicle_data(
        self,
        vehicle_id: str,
        game_version: str = "latest",
    ) -> VehicleDesc | None:
        if self.vehicle_storage is None:
            raise ValueError("Vehicle data not loaded")
        if game_version == "latest":
            if self.vehicle_latest_version is None:
                raise ValueError("Vehicle version not loaded")
            game_version = self.vehicle_latest_version
        vehicle_data = self.vehicle_storage[self.vehicle_storage["game_version"] == game_version]
        vehicle_data = vehicle_data[vehicle_data["vehicle_id"] == vehicle_id]
        if vehicle_data.empty:
            return None
        return VehicleDesc.model_validate(vehicle_data.iloc[0].to_dict())
