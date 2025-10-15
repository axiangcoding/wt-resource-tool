from pathlib import Path

import pandas as pd

from wt_resource_tool.parser.tools import clean_text, create_name_i18n_from_row
from wt_resource_tool.schema._common import Country, NameI18N
from wt_resource_tool.schema._medal import ParsedPlayerMedalData, PlayerMedalDesc

KEY_FIELD = "<ID|readonly|noverify>"


def is_medal_row(key: str) -> bool:
    """end with /name"""
    return key.endswith("/name")


def is_desc_row(key: str) -> bool:
    """end with /desc"""
    return key.endswith("/desc")


def get_medal_id_from_key(key: str) -> str:
    """Extract medal ID by removing /name or /desc suffix."""
    if key.endswith("/name"):
        return key.removesuffix("/name")
    elif key.endswith("/desc"):
        return key.removesuffix("/desc")
    return key


def guess_country_from_medal_id(medal_id: str) -> Country:
    if medal_id.startswith("usa_"):
        return "country_usa"
    elif medal_id.startswith("ge_") or medal_id.startswith("ger_"):
        return "country_germany"
    elif medal_id.startswith("ussr_"):
        return "country_ussr"
    elif medal_id.startswith("uk_") or medal_id.startswith("raaf_"):
        return "country_britain"
    elif medal_id.startswith("jap_"):
        return "country_japan"
    elif medal_id.startswith("cn_"):
        return "country_china"
    elif medal_id.startswith("it_"):
        return "country_italy"
    elif medal_id.startswith("fr_"):
        return "country_france"
    elif medal_id.startswith("sw_"):
        return "country_sweden"
    elif medal_id.startswith("il_"):
        return "country_israel"
    else:
        return "unknown"


def parse_player_medal(repo_path: str) -> ParsedPlayerMedalData:
    repo_dir = Path(repo_path)
    game_version = (repo_dir / "version").read_text(encoding="utf-8").strip()

    csv_file = repo_dir / "lang.vromfs.bin_u/lang/unlocks_medals.csv"

    df = pd.read_csv(csv_file, delimiter=";")

    # divide into medal and desc
    medal_df = df[df[KEY_FIELD].apply(is_medal_row)].copy()

    # add medal_id to both medal_df and desc_df
    medal_df["medal_id"] = medal_df[KEY_FIELD].apply(get_medal_id_from_key)
    medal_df["country"] = medal_df["medal_id"].apply(guess_country_from_medal_id)

    medal_records = medal_df.to_dict("records")
    all_medals = [
        PlayerMedalDesc(
            medal_id=record["medal_id"],
            country=record["country"],
            name_i18n=create_name_i18n_from_row(record),
            game_version=game_version,
        )
        for record in medal_records
    ]
    return ParsedPlayerMedalData(medals=all_medals)
