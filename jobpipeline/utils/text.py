from __future__ import annotations

import re


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_skill(value: str) -> str:
    key = value.lower().strip()
    synonyms = {
        "tcp ip": "tcp/ip",
        "tcpip": "tcp/ip",
        "active directory": "ad",
        "routing & switching": "routing switching",
        "panos": "palo alto",
        "paloalto": "palo alto",
    }
    return synonyms.get(key, key)
