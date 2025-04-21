import csv
from os import path

from wt_resource_tool.schema._wt_schema import Country, NameI18N, ParsedPlayerMedalData, PlayerMedalDesc


def _get_dt_from_csv(data: csv.DictReader, game_version: str) -> list[PlayerMedalDesc]:
    titles: list[PlayerMedalDesc] = []
    for row in data:
        row1 = row["<ID|readonly|noverify>"]

        if row1.endswith("/name"):
            country: Country = "unknown"
            mid = row["<ID|readonly|noverify>"].replace("/name", "")
            if mid.startswith("usa_"):
                country = "country_usa"
            elif mid.startswith("ge_") or mid.startswith("ger_"):
                country = "country_germany"
            elif mid.startswith("ussr_"):
                country = "country_ussr"
            elif mid.startswith("uk_") or mid.startswith("raaf_"):
                country = "country_britain"
            elif mid.startswith("jap_"):
                country = "country_japan"
            elif mid.startswith("cn_"):
                country = "country_china"
            elif mid.startswith("it_"):
                country = "country_italy"
            elif mid.startswith("fr_"):
                country = "country_france"
            elif mid.startswith("sw_"):
                country = "country_sweden"
            elif mid.startswith("il_"):
                country = "country_israel"
            else:
                country = "unknown"
            td = PlayerMedalDesc(
                medal_id=mid,
                country=country,
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


def parse_player_medal(repo_path: str) -> ParsedPlayerMedalData:
    all_medals: list[PlayerMedalDesc] = []
    game_version = open(path.join(repo_path, "version"), encoding="utf-8").read().strip()
    with open(path.join(repo_path, "lang.vromfs.bin_u/lang/unlocks_medals.csv"), encoding="utf-8") as f:
        data = csv.DictReader(f, delimiter=";")
        all_medals.extend(
            _get_dt_from_csv(data, game_version),
        )
    return ParsedPlayerMedalData(medals=all_medals)
