from __future__ import annotations

import re


def sanitize_text(value: object) -> str:
    text = str(value or "").strip()
    return re.sub(r"[<>]", "", text)


def sanitize_email(value: object) -> str:
    return sanitize_text(value).replace(" ", "").lower()


def sanitize_number(value: object) -> str:
    return sanitize_text(value).replace(",", "")
