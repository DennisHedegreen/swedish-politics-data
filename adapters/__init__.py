from __future__ import annotations

from importlib import import_module


def get_adapter(country_id: str):
    return import_module(f"adapters.{country_id}.adapter")
