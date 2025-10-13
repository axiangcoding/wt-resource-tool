import unicodedata

import pandas as pd


def clean_text(text: str) -> str:
    """Cleans text by removing invisible characters and trimming whitespace"""

    text = text.replace("\\t", "")
    return "".join([c for c in text if unicodedata.category(c) not in ("Cc", "Cf")])
