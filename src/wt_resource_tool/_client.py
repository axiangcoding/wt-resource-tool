import asyncio
import time
from abc import ABC, abstractmethod
from typing import Literal

import numpy as np
from deprecated import deprecated
from loguru import logger
from pandas import DataFrame

from wt_resource_tool.parser import player_medal_parser, player_title_parser, vehicle_data_parser
from wt_resource_tool.schema._medal import ParsedPlayerMedalData, PlayerMedalDesc
from wt_resource_tool.schema._title import ParsedPlayerTitleData, PlayerTitleDesc
from wt_resource_tool.schema._vehicle import ParsedVehicleData, VehicleDesc

type DataType = Literal["player_title", "player_medal", "vehicle"]


class WTResourceToolABC(ABC):
    """
    A tool to parse and get data about War Thunder.

    This class is the base class for all War Thunder resource tools.
    It provides the basic interface for parsing and getting data.

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

        tasks = []

        if "player_title" in data_types:
            logger.debug("Parsing player title data from {}", local_repo_path)

            async def parse_and_save_title():
                ts = await asyncio.to_thread(lambda: player_title_parser.parse_player_title(local_repo_path))
                await self.save_player_title_data(ts)

            tasks.append(parse_and_save_title())

        if "player_medal" in data_types:
            logger.debug("Parsing player medal data from {}", local_repo_path)

            async def parse_and_save_medal():
                ms = await asyncio.to_thread(lambda: player_medal_parser.parse_player_medal(local_repo_path))
                await self.save_player_medal_data(ms)

            tasks.append(parse_and_save_medal())

        if "vehicle" in data_types:
            logger.debug("Parsing vehicle data from {}", local_repo_path)

            async def parse_and_save_vehicle():
                vs = await asyncio.to_thread(lambda: vehicle_data_parser.parse_vehicle_data(local_repo_path))
                await self.save_vehicle_data(vs)

            tasks.append(parse_and_save_vehicle())

        # parallel run tasks
        await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        logger.info(
            f"Parsed and load data {data_types} in {round(end_time - start_time, 2)} seconds",
        )

    async def get_player_title(
        self,
        title_id: str,
        game_version: str = "latest",
    ) -> PlayerTitleDesc | None:
        """
        Get title data by id.

        """
        founds = await self.search_player_title(title_id=title_id, game_version=game_version)
        if not founds:
            return None
        return founds[0]

    async def get_player_medal(
        self,
        medal_id: str,
        game_version: str = "latest",
    ) -> PlayerMedalDesc | None:
        """
        Get medal data by id.

        """
        founds = await self.search_player_medal(medal_id=medal_id, game_version=game_version)
        if not founds:
            return None
        return founds[0]

    async def get_vehicle(
        self,
        vehicle_id: str,
        game_version: str = "latest",
    ) -> VehicleDesc | None:
        """
        Get vehicle data by id.

        """
        founds = await self.search_vehicle(vehicle_id=vehicle_id, game_version=game_version)
        if not founds:
            return None
        return founds[0]

    @abstractmethod
    async def search_player_title(
        self,
        title_id: str | None = None,
        game_version: str = "latest",
    ) -> list[PlayerTitleDesc]:
        """
        Search title data by filter.

        Args:
            title_id (str | None): The title id to filter. If None, return all titles.
            game_version (str): The game version to filter. Default is "latest".
        """
        raise NotImplementedError("search_player_title not implemented")

    @abstractmethod
    async def search_player_medal(
        self,
        medal_id: str | None = None,
        country: str | None = None,
        game_version: str = "latest",
    ) -> list[PlayerMedalDesc]:
        """
        Search medal data by filter.

        Args:
            medal_id (str | None): The medal id to filter. If None, return all medals.
            country (str | None): The country to filter. If None, return all countries.
            game_version (str): The game version to filter. Default is "latest".
        """
        raise NotImplementedError("search_player_medal not implemented")

    @abstractmethod
    async def search_vehicle(
        self,
        vehicle_id: str | None = None,
        country: str | None = None,
        game_version: str = "latest",
    ) -> list[VehicleDesc]:
        """
        Search vehicle data by filter.

        Args:
            vehicle_id (str | None): The vehicle id to filter. If None, return all vehicles.
            country (str | None): The country to filter. If None, return all countries.
            game_version (str): The game version to filter. Default is "latest".

        """
        raise NotImplementedError("search_vehicle not implemented")

    @abstractmethod
    async def save_player_title_data(
        self,
        title_data: ParsedPlayerTitleData,
    ):
        """Save title data to storage"""
        raise NotImplementedError("save_player_title_data not implemented")

    @abstractmethod
    async def save_player_medal_data(
        self,
        medal_data: ParsedPlayerMedalData,
    ):
        """Save medal data to storage"""
        raise NotImplementedError("save_player_medal_data not implemented")

    @abstractmethod
    async def save_vehicle_data(
        self,
        vehicle_data: ParsedVehicleData,
    ):
        """Save vehicle data to storage"""
        raise NotImplementedError("save_vehicle_data not implemented")


class WTResourceToolMemory(WTResourceToolABC):
    """A tool to parse and get data about War Thunder.

    This class stores the data in memory.
    """

    def __init__(self) -> None:
        super().__init__()
        self.player_title_storage: DataFrame | None = None
        self.player_title_latest_version: str | None = None
        self.player_medal_storage: DataFrame | None = None
        self.player_medal_latest_version: str | None = None
        self.vehicle_storage: DataFrame | None = None
        self.vehicle_latest_version: str | None = None

    async def search_player_title(
        self,
        title_id: str | None = None,
        game_version: str = "latest",
    ) -> list[PlayerTitleDesc]:
        if self.player_title_storage is None or self.player_title_latest_version is None:
            raise ValueError("Player title data not loaded")
        if game_version == "latest":
            game_version = self.player_title_latest_version
        df = self.player_title_storage

        query_conditions = ["game_version == @game_version"]
        if title_id is not None:
            query_conditions.append("title_id == @title_id")

        query_str = " and ".join(query_conditions)
        df_result = df.query(query_str)

        if df_result.empty:
            return []
        return [PlayerTitleDesc.model_validate(item) for item in df_result.to_dict(orient="records")]

    async def search_player_medal(
        self,
        medal_id: str | None = None,
        country: str | None = None,
        game_version: str = "latest",
    ) -> list[PlayerMedalDesc]:
        if self.player_medal_storage is None or self.player_medal_latest_version is None:
            raise ValueError("Player medal data not loaded")
        if game_version == "latest":
            game_version = self.player_medal_latest_version
        df = self.player_medal_storage

        query_conditions = ["game_version == @game_version"]
        if medal_id is not None:
            query_conditions.append("medal_id == @medal_id")
        if country is not None:
            query_conditions.append("country == @country")

        query_str = " and ".join(query_conditions)
        df_result = df.query(query_str)

        if df_result.empty:
            return []
        return [PlayerMedalDesc.model_validate(item) for item in df_result.to_dict(orient="records")]

    async def search_vehicle(
        self,
        vehicle_id: str | None = None,
        country: str | None = None,
        game_version: str = "latest",
    ) -> list[VehicleDesc]:
        if self.vehicle_storage is None or self.vehicle_latest_version is None:
            raise ValueError("Vehicle data not loaded")
        if game_version == "latest":
            game_version = self.vehicle_latest_version
        df = self.vehicle_storage

        query_conditions = ["game_version == @game_version"]
        if vehicle_id is not None:
            query_conditions.append("vehicle_id == @vehicle_id")
        if country is not None:
            query_conditions.append("country == @country")

        query_str = " and ".join(query_conditions)
        df_result = df.query(query_str)

        if df_result.empty:
            return []
        return [VehicleDesc.model_validate(item) for item in df_result.to_dict(orient="records")]

    async def save_player_title_data(self, title_data: ParsedPlayerTitleData):
        df = DataFrame([item.model_dump() for item in title_data.titles])
        self.player_title_storage = df
        self.player_title_latest_version = title_data.titles[0].game_version

    async def save_player_medal_data(self, medal_data: ParsedPlayerMedalData):
        self.player_medal_storage = DataFrame([item.model_dump() for item in medal_data.medals])
        self.player_medal_latest_version = medal_data.medals[0].game_version

    async def save_vehicle_data(self, vehicle_data: ParsedVehicleData):
        df = DataFrame([item.model_dump() for item in vehicle_data.vehicles])
        df = df.replace({np.nan: None})
        self.vehicle_storage = df
        self.vehicle_latest_version = vehicle_data.vehicles[0].game_version
