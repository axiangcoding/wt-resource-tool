import os

from dotenv import load_dotenv

from wt_resource_tool.parser import player_title_parser

if __name__ == "__main__":
    load_dotenv()
    repo_path = os.environ["DATAMINE_REPO_PATH"]
    pt_storage = player_title_parser.parse_player_title(repo_path)

    version_folder = os.path.join("static/", pt_storage.game_version.replace(".", "_"))
    latest_folder = os.path.join("static/latest")
    os.makedirs(version_folder, exist_ok=True)
    os.makedirs(latest_folder, exist_ok=True)

    json_content = pt_storage.model_dump_json(indent=2)
    with open(os.path.join(latest_folder, "player_title.json"), "w", encoding="utf-8") as f:
        f.write(json_content)
