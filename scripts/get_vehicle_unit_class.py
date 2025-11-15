import os

from dotenv import load_dotenv

from wt_resource_tool.parser.vehicle_data_parser import parse_vehicle_data

load_dotenv()

repo_path = os.getenv("DATAMINE_REPO_PATH")
if not repo_path:
    raise ValueError("Environment variable DATAMINE_REPO_PATH is not set.")
vehicles = parse_vehicle_data(repo_path)

unit_classes = set()

for vehicle in vehicles.vehicles:
    unit_classes.add(vehicle.unit_class)

for unit_class in sorted(unit_classes):
    print(unit_class)
