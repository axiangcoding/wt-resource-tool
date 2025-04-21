import csv
import json
import keyword
from os import path
from typing import Any

from loguru import logger

from wt_resource_tool.schema._wt_schema import ParsedVehicleData, VehicleDesc


def get_lang_units_data(repo_path: str) -> dict[str, dict[str, str]]:
    units_path = path.join(repo_path, "lang.vromfs.bin_u", "lang", "units.csv")
    with open(units_path, encoding="utf-8") as f:
        lang_units = f.read()
    data = csv.DictReader(lang_units.splitlines(), delimiter=";")
    result: dict[str, dict[str, str]] = {}
    for row in data:
        result[row["<ID|readonly|noverify>"]] = {
            "english": row["<English>"],
            "french": row["<French>"],
            "italian": row["<Italian>"],
            "german": row["<German>"],
            "spanish": row["<Spanish>"],
            "japanese": row["<Japanese>"].replace("\\t", ""),
            "chinese": row["<Chinese>"].replace("\\t", ""),
            "russian": row["<Russian>"],
        }
    return result


def parse_vehicle_data(repo_path: str) -> ParsedVehicleData:
    game_version = open(path.join(repo_path, "version"), encoding="utf-8").read().strip()

    wpcost_path = path.join(repo_path, "char.vromfs.bin_u", "config", "wpcost.blkx")
    with open(wpcost_path, encoding="utf-8") as f:
        wpcost = f.read()

    data: dict = json.loads(wpcost)
    convert_key_map = {
        "rank": "rank",
        "economicRankArcade": "economic_rank_arcade",
        "economicRankHistorical": "economic_rank_historical",
        "economicRankSimulation": "economic_rank_simulation",
        "country": "country",
        "unitClass": "unit_class",
        "spawnType": "spawn_type",
        "value": "value",
        "reqExp": "req_exp",
        "trainCost": "train_cost",
        "train2Cost": "train2_cost",
        "train3Cost_gold": "train3_cost_gold",
        "train3Cost_exp": "train3_cost_exp",
        "repairCostArcade": "repair_cost_arcade",
        "repairCostHistorical": "repair_cost_historical",
        "repairCostSimulation": "repair_cost_simulation",
        "repairCostPerMinArcade": "repair_cost_per_min_arcade",
        "repairCostPerMinHistorical": "repair_cost_per_min_historical",
        "repairCostPerMinSimulation": "repair_cost_per_min_simulation",
        "repairCostFullUpgradedArcade": "repair_cost_full_upgraded_arcade",
        "repairCostFullUpgradedHistorical": "repair_cost_full_upgraded_historical",
        "repairCostFullUpgradedSimulation": "repair_cost_full_upgraded_simulation",
        "rewardMulArcade": "reward_mul_arcade",
        "rewardMulHistorical": "reward_mul_historical",
        "rewardMulSimulation": "reward_mul_simulation",
        "expMul": "exp_mul",
        "reqAir": "req_air",
        "reloadTime_cannon": "reload_time_cannon",
        "crewTotalCount": "crew_total_count",
        "primaryWeaponAutoLoader": "primary_weapon_auto_loader",
        "costGold": "cost_gold",
        "turretSpeed": "turret_speed",
        "gift": "gift",
        "researchType": "research_type",
        "economicRankTankHistorical": "economic_rank_tank_historical",
        "economicRankTankSimulation": "economic_rank_tank_simulation",
    }

    lang_units = get_lang_units_data(repo_path)

    vehicles: list[VehicleDesc] = []
    for key in data.keys():
        if not isinstance(data[key], dict):
            logger.warning(f"key {key} is not a dict, so it's not vehicle data, skip")
            continue
        try:
            v_data: dict = data[key]
            n_data = {
                "vehicle_id": key,
                "name_shop_i18n": lang_units.get(f"{key}_shop"),
                "name_0_i18n": lang_units.get(f"{key}_0"),
                "name_1_i18n": lang_units.get(f"{key}_1"),
                "name_2_i18n": lang_units.get(f"{key}_2"),
                "game_version": game_version,
            }

            for k, v in v_data.items():
                if k in convert_key_map:
                    n_data[convert_key_map[k]] = v
                else:
                    n_data[k] = v

            vehicles.append(VehicleDesc.model_validate(n_data))
        except Exception as e:
            logger.warning("error when parsing vehicle id: {}, skip", key)
            raise e
    return ParsedVehicleData(vehicles=vehicles)
