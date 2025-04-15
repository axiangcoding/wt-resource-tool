import os

from dotenv import load_dotenv

from wt_resource_tool.parser import vehicle_data_parser

if __name__ == "__main__":
    load_dotenv()
    repo_path = os.environ["DATAMINE_REPO_PATH"]
    v_storage = vehicle_data_parser.parse_vehicle_data(repo_path)

    latest_folder = os.path.join("static/latest")
    os.makedirs(latest_folder, exist_ok=True)

    json_content = v_storage.model_dump_json(indent=2)
    with open(os.path.join(latest_folder, "vehicle_data.json"), "w", encoding="utf-8") as f:
        f.write(json_content)
