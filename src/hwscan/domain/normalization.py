from __future__ import annotations

import re
from typing import Any

PLACEHOLDER_IDENTIFIERS = {
    "",
    "default string",
    "none",
    "not specified",
    "system serial number",
    "to be filled by o.e.m.",
    "unknown",
}


def clean_text(value: Any, *, maximum_length: int = 512) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).replace("\x00", " ").split())[:maximum_length]
    return text or None


def clean_identifier(value: Any) -> str | None:
    text = clean_text(value, maximum_length=256)
    if text is None or text.casefold() in PLACEHOLDER_IDENTIFIERS:
        return None
    compact = re.sub(r"[^0-9a-f]", "", text.casefold())
    if compact and set(compact) == {"0"}:
        return None
    return text


def integer_or_none(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


def percentage(numerator: Any, denominator: Any) -> float | None:
    top = integer_or_none(numerator)
    bottom = integer_or_none(denominator)
    if top is None or bottom is None or top < 0 or bottom <= 0:
        return None
    return round(top / bottom * 100, 1)


def safe_filename_component(value: Any, *, fallback: str = "UNKNOWN") -> str:
    text = clean_text(value, maximum_length=80) or fallback
    normalized = re.sub(r"[^A-Za-z0-9_-]+", "-", text).strip("-_")
    return normalized or fallback


def excel_safe_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    cleaned = clean_text(value, maximum_length=32767) or ""
    if cleaned.startswith(("=", "+", "-", "@")):
        return "'" + cleaned
    return cleaned
