import unicodedata


def clean_text(text: str) -> str:
    """Cleans text by removing invisible characters and trimming whitespace"""
    return "".join([c for c in text if unicodedata.category(c) not in ("Cc", "Cf")])
