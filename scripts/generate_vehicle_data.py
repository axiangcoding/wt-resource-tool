import csv
import json
import os
from typing import Any

from dotenv import load_dotenv
from loguru import logger

from wt_resource_tool._schema import Vehicle, VehicleStorage


def _read_vehicle_data() -> VehicleStorage:
    repo_path = os.environ["DATAMINE_REPO_PATH"]
    game_version = open(os.path.join(repo_path, "version"), encoding="utf-8").read()

    wpcost_path = os.path.join(repo_path, "char.vromfs.bin_u", "config", "wpcost.blkx")
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

    vehicles = {}
    for key in data.keys():
        if not isinstance(data[key], dict):
            logger.warning("key {} is not a dict, skip.", key)
            continue
        try:
            v_data: dict = data[key]
            n_data = {
                "id": key,
            }

            for k, v in v_data.items():
                if k in convert_key_map:
                    n_data[convert_key_map[k]] = v
                else:
                    n_data[k] = v

            # n_data["vehicle_name_cn_shop"] = (
            #     translate_data[f"{key}_shop"]["Chinese"] if f"{key}_shop" in translate_data else key
            # )
            # n_data["vehicle_name_cn_0"] = translate_data[f"{key}_0"]["Chinese"] if f"{key}_0" in translate_data else key
            # n_data["vehicle_name_cn_1"] = translate_data[f"{key}_1"]["Chinese"] if f"{key}_1" in translate_data else key
            # n_data["vehicle_name_cn_2"] = translate_data[f"{key}_2"]["Chinese"] if f"{key}_2" in translate_data else key
            vehicles[key] = Vehicle.model_validate(n_data)
        except Exception as e:
            logger.warning("error when parsing vehicle id: {}, skip", key)
            raise e
    return VehicleStorage(vehicles_map=vehicles, game_version=game_version.strip())


if __name__ == "__main__":
    load_dotenv()
    v_storage = _read_vehicle_data()

    version_folder = os.path.join("static/", v_storage.game_version.replace(".", "_"))
    latest_folder = os.path.join("static/latest")
    os.makedirs(version_folder, exist_ok=True)
    os.makedirs(latest_folder, exist_ok=True)

    json_content = v_storage.model_dump_json(indent=2)
    with open(os.path.join(latest_folder, "vehicle.json"), "w", encoding="utf-8") as f:
        f.write(json_content)
