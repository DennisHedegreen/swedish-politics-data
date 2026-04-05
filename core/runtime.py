from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

from profiles import ProfileConfig, get_profile


def parse_env_country_ids(raw_value: str | None) -> tuple[str, ...] | None:
    if not raw_value:
        return None
    parsed = tuple(item.strip().lower() for item in raw_value.split(",") if item.strip())
    return parsed or None


@dataclass(frozen=True)
class RuntimeContext:
    profile: ProfileConfig
    app_title: str
    requested_country_ids: tuple[str, ...] | None
    data_variant: str
    embedded_mode: bool


def resolve_runtime_context(
    *,
    env: dict[str, str] | None = None,
    query_params: object | None = None,
) -> RuntimeContext:
    active_env = os.environ if env is None else env
    profile = get_profile(active_env.get("WPD_PROFILE"))
    app_title = profile.title
    requested_country_ids = profile.country_ids

    explicit_title = active_env.get("WPD_APP_TITLE")
    explicit_country_ids = parse_env_country_ids(active_env.get("WPD_EXPOSE_COUNTRIES"))
    data_variant = str(active_env.get("WPD_DATA_VARIANT", "")).strip().lower()

    if explicit_title:
        app_title = explicit_title
    if explicit_country_ids is not None:
        requested_country_ids = explicit_country_ids

    embedded_raw = ""
    if query_params is not None:
        try:
            embedded_raw = str(query_params.get("embedded", ""))
        except Exception:
            embedded_raw = ""

    embedded_mode = embedded_raw.lower() in {"1", "true", "yes"}
    return RuntimeContext(
        profile=profile,
        app_title=app_title,
        requested_country_ids=requested_country_ids,
        data_variant=data_variant,
        embedded_mode=embedded_mode,
    )


def resolve_requested_country_id(
    available_country_ids: Iterable[str],
    *,
    requested_country_id: str | None,
) -> str | None:
    available = list(available_country_ids)
    if not available:
        return None
    default_country_id = available[0] if len(available) == 1 else "denmark"
    if default_country_id not in available:
        default_country_id = available[0]
    requested = str(requested_country_id or default_country_id).strip().lower() or default_country_id
    if requested not in available:
        requested = default_country_id
    return requested
