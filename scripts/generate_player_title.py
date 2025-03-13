import csv
import os
import httpx
from wt_resource_tool._schema import TitleDesc, WTPlayerTitleStorage


def _get_dt_from_csv(data: csv.DictReader) -> list[TitleDesc]:
    titles: list[TitleDesc] = []
    for row in data:
        row1 = row["<ID|readonly|noverify>"]

        if row1.startswith("title/") and (not row1.endswith("/desc")):
            id = row["<ID|readonly|noverify>"].replace("title/", "")
            english = row["<English>"]
            chinese = row["<Chinese>"].replace("\\t", "")
            russian = row["<Russian>"]

            td = TitleDesc(
                id=id,
                english=english,
                chinese=chinese,
                russian=russian,
                comments=row["<Comments>"],
                max_chars=row["<max_chars>"],
            )
            titles.append(td)
    return titles


def parse_player_title() -> WTPlayerTitleStorage:
    resource_prefix = "https://raw.githubusercontent.com/gszabi99/War-Thunder-Datamine/refs/heads/master"

    all_titles: list[TitleDesc] = []

    resp = httpx.get(
        f"{resource_prefix}/regional.vromfs.bin_u/lang/regional_titles.csv"
    )
    content = resp.text

    data = csv.DictReader(content.splitlines(), delimiter=";")
    all_titles.extend(_get_dt_from_csv(data))

    resp = httpx.get(
        f"{resource_prefix}/lang.vromfs.bin_u/lang/unlocks_achievements.csv"
    )
    content = resp.text

    data = csv.DictReader(content.splitlines(), delimiter=";")
    all_titles.extend(_get_dt_from_csv(data))

    resp = httpx.get(f"{resource_prefix}/regional.vromfs.bin_u/lang/tournaments.csv")
    content = resp.text

    data = csv.DictReader(content.splitlines(), delimiter=";")
    all_titles.extend(_get_dt_from_csv(data))

    title_map = {}
    for title in all_titles:
        title_map[title.id] = title

    game_version = httpx.get(f"{resource_prefix}/version").text

    return WTPlayerTitleStorage(titles_map=title_map, game_version=game_version.strip())


if __name__ == "__main__":
    pt_storage = parse_player_title()

    version_folder = os.path.join("static/", pt_storage.game_version.replace(".", "_"))
    latest_folder = os.path.join("static/latest")
    os.makedirs(version_folder, exist_ok=True)
    os.makedirs(latest_folder, exist_ok=True)

    json_content = pt_storage.model_dump_json(indent=2)
    with open(
        os.path.join(version_folder, "player_title.json"), "w", encoding="utf-8"
    ) as f:
        f.write(json_content)
    with open(
        os.path.join(latest_folder, "player_title.json"), "w", encoding="utf-8"
    ) as f:
        f.write(json_content)
