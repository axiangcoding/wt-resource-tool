import re
import unicodedata
from typing import Any

from wt_resource_tool.schema._common import NameI18N


def clean_text(text: str) -> str:
    """Cleans text by removing invisible characters and trimming whitespace"""

    text = text.replace("\\t", "")
    return "".join([c for c in text if unicodedata.category(c) not in ("Cc", "Cf")])


def camel_to_snake(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case"""
    s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)

    s2 = re.sub("([A-Z])([A-Z][a-z])", r"\1_\2", s1)
    return s2.lower()


def convert_keys_to_snake_case(data) -> Any:
    """Recursively convert all dictionary keys from camelCase to snake_case"""
    if isinstance(data, dict):
        return {camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


def create_name_i18n_from_row(row) -> NameI18N:
    """Create NameI18N object from a DataFrame row"""
    return NameI18N(
        english=row["<English>"],
        french=row["<French>"],
        italian=row["<Italian>"],
        german=row["<German>"],
        spanish=row["<Spanish>"],
        japanese=clean_text(row["<Japanese>"]),
        chinese=clean_text(row["<Chinese>"]),
        russian=row["<Russian>"],
        h_chinese=clean_text(row["<HChinese>"]),
        t_chinese=clean_text(row["<TChinese>"]),
    )
