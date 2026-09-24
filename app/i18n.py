from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent / "locales"
DEFAULT_LANGUAGE = "ca"

LANGUAGES = {
    "ca": "Català",
    "es": "Español",
    "en": "English",
    "eu": "Euskara",
    "gl": "Galego",
}


@lru_cache(maxsize=None)
def load_language(code: str) -> dict[str, str]:
    path = LOCALES_DIR / f"{code}.json"
    if not path.exists():
        path = LOCALES_DIR / f"{DEFAULT_LANGUAGE}.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=1)
def _fallback() -> dict[str, str]:
    return load_language(DEFAULT_LANGUAGE)


def translator(code: str):
    data = load_language(code)
    fallback = _fallback()

    def t(key: str, **kwargs) -> str:
        text = data.get(key, fallback.get(key, key))
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text

    return t
