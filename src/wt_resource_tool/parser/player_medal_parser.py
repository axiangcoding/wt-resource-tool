import csv
from os import path

from wt_resource_tool.schema._wt_schema import PlayerMedalDesc, PlayerMedalStorage


def _get_dt_from_csv(data: csv.DictReader) -> list[PlayerMedalDesc]:
    titles: list[PlayerMedalDesc] = []
    for row in data:
        row1 = row["<ID|readonly|noverify>"]

        if row1.endswith("/name"):
            mid = row["<ID|readonly|noverify>"].replace("/name", "")

            td = PlayerMedalDesc(
                id=mid,
                english=row["<English>"],
                french=row["<French>"],
                italian=row["<Italian>"],
                german=row["<German>"],
                spanish=row["<Spanish>"],
                japanese=row["<Japanese>"].replace("\\t", ""),
                chinese=row["<Chinese>"].replace("\\t", ""),
                russian=row["<Russian>"],
                comments=row["<Comments>"],
                max_chars=row["<max_chars>"],
            )
            titles.append(td)
    return titles


def parse_player_medal(repo_path: str) -> PlayerMedalStorage:
    all_medals: list[PlayerMedalDesc] = []

    with open(path.join(repo_path, "lang.vromfs.bin_u/lang/unlocks_medals.csv"), encoding="utf-8") as f:
        data = csv.DictReader(f, delimiter=";")
        all_medals.extend(_get_dt_from_csv(data))

    medals_map = {}
    for title in all_medals:
        medals_map[title.id] = title

    game_version = open(path.join(repo_path, "version"), encoding="utf-8").read()
    return PlayerMedalStorage(medals_map=medals_map, game_version=game_version.strip())
