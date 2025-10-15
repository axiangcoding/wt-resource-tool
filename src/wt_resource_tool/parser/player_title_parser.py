from pathlib import Path

import pandas as pd
from pandas import DataFrame

from wt_resource_tool.parser.tools import clean_text, create_name_i18n_from_row
from wt_resource_tool.schema._common import NameI18N
from wt_resource_tool.schema._title import ParsedPlayerTitleData, PlayerTitleDesc

KEY_FIELD = "<ID|readonly|noverify>"


def is_title_row(key: str) -> bool:
    """start with title/ or title_, and not end with /desc"""
    return key.startswith("title") and not key.endswith("/desc")


def is_desc_row(key: str) -> bool:
    """end with /desc"""
    return key.startswith("title") and key.endswith("/desc")


def get_title_id_from_key(key: str) -> str:
    """Extract title ID by removing title/ prefix and /desc suffix."""
    key = key.removeprefix("title/")
    return key.removesuffix("/desc")


def parse_player_title(repo_path: str) -> ParsedPlayerTitleData:
    repo_dir = Path(repo_path)
    game_version = (repo_dir / "version").read_text(encoding="utf-8").strip()

    all_titles: list[PlayerTitleDesc] = []

    csv_files = [
        repo_dir / "regional.vromfs.bin_u/lang/regional_titles.csv",
        repo_dir / "lang.vromfs.bin_u/lang/unlocks_achievements.csv",
        repo_dir / "regional.vromfs.bin_u/lang/tournaments.csv",
    ]

    dfs: list[DataFrame] = []
    for csv_file in csv_files:
        dfs.append(pd.read_csv(csv_file, delimiter=";"))
    df = pd.concat(dfs, ignore_index=True)

    # divide into title and desc
    title_df = df[df[KEY_FIELD].apply(is_title_row)].copy()
    desc_df = df[df[KEY_FIELD].apply(is_desc_row)].copy()

    # add title_id to both title_df and desc_df
    title_df["title_id"] = title_df[KEY_FIELD].apply(get_title_id_from_key)

    desc_df["title_id"] = desc_df[KEY_FIELD].apply(get_title_id_from_key)

    # filter out desc rows with any missing language data
    lang_columns = [
        "<English>",
        "<French>",
        "<Italian>",
        "<German>",
        "<Spanish>",
        "<Japanese>",
        "<Chinese>",
        "<Russian>",
        "<HChinese>",
        "<TChinese>",
    ]
    desc_df = desc_df.dropna(subset=lang_columns)

    # create description mapping using vectorized operations
    # Convert desc_df to records for faster processing
    desc_records = desc_df.to_dict("records")
    desc_map = {record["title_id"]: create_name_i18n_from_row(record) for record in desc_records}

    # create title list using vectorized operations
    # Convert title_df to records for faster processing
    title_records = title_df.to_dict("records")
    all_titles = [
        PlayerTitleDesc(
            title_id=record["title_id"],
            description_i18n=desc_map.get(record["title_id"]),
            name_i18n=create_name_i18n_from_row(record),
            game_version=game_version,
        )
        for record in title_records
    ]
    return ParsedPlayerTitleData(titles=all_titles)
