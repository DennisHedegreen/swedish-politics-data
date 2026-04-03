from __future__ import annotations

from pathlib import Path


def resolve_sweden_public_path(relative_path: str, variant: str = "") -> Path:
    active_variant = str(variant or "").strip().lower()
    if active_variant:
        return Path("tests/app-failure-states/app-fixtures") / active_variant / relative_path
    return Path("sweden") / relative_path
