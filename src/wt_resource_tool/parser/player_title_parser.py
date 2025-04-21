import csv
from os import path

from wt_resource_tool.schema._wt_schema import NameI18N, ParsedPlayerTitleData, PlayerTitleDesc


def _get_dt_from_csv(data: csv.DictReader, game_version: str) -> list[PlayerTitleDesc]:
    titles: list[PlayerTitleDesc] = []
    for row in data:
        row1 = row["<ID|readonly|noverify>"]

        if row1.startswith("title/") and (not row1.endswith("/desc")):
            mid = row["<ID|readonly|noverify>"].replace("title/", "")
            td = PlayerTitleDesc(
                title_id=mid,
                name_i18n=NameI18N(
                    english=row["<English>"],
                    french=row["<French>"],
                    italian=row["<Italian>"],
                    german=row["<German>"],
                    spanish=row["<Spanish>"],
                    japanese=row["<Japanese>"].replace("\\t", ""),
                    chinese=row["<Chinese>"].replace("\\t", ""),
                    russian=row["<Russian>"],
                ),
                game_version=game_version,
            )
            titles.append(td)
    return titles


def parse_player_title(repo_path: str) -> ParsedPlayerTitleData:
    all_titles: list[PlayerTitleDesc] = []
    game_version = open(path.join(repo_path, "version"), encoding="utf-8").read().strip()
    with open(path.join(repo_path, "regional.vromfs.bin_u/lang/regional_titles.csv"), encoding="utf-8") as f:
        data = csv.DictReader(f, delimiter=";")
        all_titles.extend(_get_dt_from_csv(data, game_version))

    with open(path.join(repo_path, "lang.vromfs.bin_u/lang/unlocks_achievements.csv"), encoding="utf-8") as f:
        data = csv.DictReader(f, delimiter=";")
        all_titles.extend(_get_dt_from_csv(data, game_version))

    with open(path.join(repo_path, "regional.vromfs.bin_u/lang/tournaments.csv"), encoding="utf-8") as f:
        data = csv.DictReader(f, delimiter=";")
        all_titles.extend(_get_dt_from_csv(data, game_version))

    return ParsedPlayerTitleData(titles=all_titles)
