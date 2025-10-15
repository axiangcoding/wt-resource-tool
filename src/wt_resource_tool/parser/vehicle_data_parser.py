import json
from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from wt_resource_tool.parser.tools import camel_to_snake, create_name_i18n_from_row
from wt_resource_tool.schema._common import NameI18N
from wt_resource_tool.schema._vehicle import ParsedVehicleData, VehicleDesc


def _get_units_lang_dict(repo_dir: Path) -> dict[str, NameI18N]:
    units_lang_path = repo_dir / "lang.vromfs.bin_u/lang/units.csv"

    lang_units_df = pd.read_csv(units_lang_path, delimiter=";")

    # filter out desc rows with any missing language data
    lang_columns = [
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
    lang_units_df = lang_units_df.dropna(subset=lang_columns)

    result: dict[str, NameI18N] = {}
    for _, row in lang_units_df.iterrows():
        result[row["<ID|readonly|noverify>"]] = create_name_i18n_from_row(row)
    return result


def parse_vehicle_data(repo_path: str) -> ParsedVehicleData:
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
                n_data[camel_to_snake(k)] = v

            vehicles.append(VehicleDesc.model_validate(n_data))
        except Exception as e:
            logger.warning("error when parsing vehicle id: {}, skip", key)
            raise e

    return ParsedVehicleData(vehicles=vehicles, max_economic_rank=max_economic_rank)
