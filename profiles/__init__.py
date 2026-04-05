from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileConfig:
    name: str
    title: str
    country_ids: tuple[str, ...]
    allow_internal: bool = False


PROFILES = {
    "world_public": ProfileConfig(
        name="world_public",
        title="World Politics Data",
        country_ids=("denmark", "sweden"),
        allow_internal=False,
    ),
    "denmark_only": ProfileConfig(
        name="denmark_only",
        title="Danish Politics Data",
        country_ids=("denmark",),
        allow_internal=False,
    ),
    "sweden_only": ProfileConfig(
        name="sweden_only",
        title="Swedish Politics Data",
        country_ids=("sweden",),
        allow_internal=False,
    ),
    "world_internal": ProfileConfig(
        name="world_internal",
        title="World Politics Data",
        country_ids=("denmark", "sweden", "norway"),
        allow_internal=True,
    ),
    "denmark_norway": ProfileConfig(
        name="denmark_norway",
        title="World Politics Data",
        country_ids=("denmark", "norway"),
        allow_internal=True,
    ),
}


DEFAULT_PROFILE_NAME = "world_public"


def get_profile(name: str | None) -> ProfileConfig:
    key = str(name or DEFAULT_PROFILE_NAME).strip().lower() or DEFAULT_PROFILE_NAME
    return PROFILES.get(key, PROFILES[DEFAULT_PROFILE_NAME])
