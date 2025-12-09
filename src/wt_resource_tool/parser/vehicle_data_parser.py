import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from wt_resource_tool.parser.tools import camel_to_snake, convert_keys_to_snake_case, create_name_i18n_from_row
from wt_resource_tool.schema._common import NameI18N
from wt_resource_tool.schema._vehicle import FlightModel, ParsedVehicleData, ShipModel, TankModel, VehicleDesc

LANG_COLUMNS = [
    "<English>",
    "<French>",
    "<Italian>",
    "<German>",
    "<Spanish>",
    "<Japanese>",
    "<Chinese>",
    "<Russian>",
    "<HChinese>",
    "<TChinese>",
]


def _get_units_lang_dict(repo_dir: Path) -> dict[str, NameI18N]:
    units_lang_path = repo_dir / "lang.vromfs.bin_u/lang/units.csv"

    lang_units_df = pd.read_csv(units_lang_path, delimiter=";")

    lang_units_df = lang_units_df.dropna(subset=LANG_COLUMNS)

    result: dict[str, NameI18N] = {}
    for _, row in lang_units_df.iterrows():
        result[row["<ID|readonly|noverify>"]] = create_name_i18n_from_row(row)
    return result


def _read_model_info(repo_dir: Path, vehicle: VehicleDesc) -> tuple[str, FlightModel | TankModel | ShipModel | None]:
    base_path = Path(repo_dir / "aces.vromfs.bin_u/gamedata")
    vehicle_id = vehicle.vehicle_id

    if vehicle.unit_class_type == "air":
        air_path = base_path / f"flightmodels/{vehicle_id}.blkx"
        if air_path.exists():
            with air_path.open(encoding="utf-8") as f:
                data = json.load(f)
            model_info = FlightModel.model_validate(convert_keys_to_snake_case(data))
            return vehicle_id, model_info
    # TODO: implement tank and ship model reading
    elif vehicle.unit_class_type == "ground":
        ...
    elif vehicle.unit_class_type == "naval":
        ...
    return vehicle_id, None


def parse_vehicle_data(
    repo_path: str,
    read_model_info: bool = False,
    max_workers: int | None = None,
) -> ParsedVehicleData:
    """Parse vehicle data from the given repository path.

    TODO: model info parser still broken, do not use parameter `read_model_info` and `max_workers` for now.

    Args:
        repo_path (str): Path to the repository containing vehicle data.
        read_model_info (bool): Whether to read detailed model information for each vehicle.
        max_workers (int | None): Maximum number of worker threads to use when reading model info.

    """

    repo_dir = Path(repo_path)

    lang_units = _get_units_lang_dict(repo_dir)

    game_version = (repo_dir / "version").read_text(encoding="utf-8").strip()

    wp_cost_path = repo_dir / "char.vromfs.bin_u/config/wpcost.blkx"
    with wp_cost_path.open(encoding="utf-8") as f:
        vehicle_data: dict[str, Any] = json.load(f)

    # remove invalid key "economicRankMax"
    max_economic_rank = vehicle_data.pop("economicRankMax", None)

    vehicles: list[VehicleDesc] = []
    for key in vehicle_data.keys():
        try:
            v_data: dict = vehicle_data[key]
            n_data = {
                "vehicle_id": key,
                "name_shop_i18n": lang_units.get(f"{key}_shop"),
                "name_0_i18n": lang_units.get(f"{key}_0"),
                "name_1_i18n": lang_units.get(f"{key}_1"),
                "name_2_i18n": lang_units.get(f"{key}_2"),
                "game_version": game_version,
            }

            for k, v in v_data.items():
                n_data[camel_to_snake(k)] = convert_keys_to_snake_case(v)

            vehicles.append(VehicleDesc.model_validate(n_data))
        except Exception as e:
            logger.warning("error when parsing vehicle id: {}, skip", key)
            raise e

    if read_model_info:
        # add model info using thread pool
        logger.info(f"Reading model info for {len(vehicles)} vehicles using thread pool")

        model_info_dict: dict[str, FlightModel | TankModel | ShipModel | None] = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_read_model_info, repo_dir, vehicle) for vehicle in vehicles]
            completed_count = 0
            for future in as_completed(futures):
                try:
                    vehicle_id, model_info = future.result()
                    model_info_dict[vehicle_id] = model_info

                    completed_count += 1
                    if completed_count % 1000 == 0:
                        logger.info(f"Processed {completed_count}/{len(vehicles)} vehicles")
                except Exception as e:
                    logger.error(f"Error processing vehicle: {e}")

        logger.info(f"Completed reading model info for all {len(vehicles)} vehicles")

        updated_vehicles: list[VehicleDesc] = []
        for vehicle in vehicles:
            model_info = model_info_dict.get(vehicle.vehicle_id)
            if model_info is None:
                updated_vehicles.append(vehicle)
            else:
                if isinstance(model_info, FlightModel):
                    vehicle.flight_model = model_info
                elif isinstance(model_info, TankModel):
                    vehicle.tank_model = model_info
                elif isinstance(model_info, ShipModel):
                    vehicle.ship_model = model_info
                updated_vehicles.append(vehicle)
        vehicles = updated_vehicles
    return ParsedVehicleData(vehicles=vehicles, max_economic_rank=max_economic_rank, game_version=game_version)
