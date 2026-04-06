from __future__ import annotations

from typing import Mapping

import pandas as pd


def classify_public_data_state(
    has_municipal_votes: bool,
    factor_files_expected: int,
    factor_files_with_rows: int,
) -> str:
    if not has_municipal_votes:
        return "missing_election_data"
    if factor_files_expected == 0 or factor_files_with_rows == 0:
        return "missing_factor_data"
    if factor_files_with_rows < factor_files_expected:
        return "partial_factor_data"
    return "ready"


def summarize_public_data_state(
    municipal_df: pd.DataFrame,
    national_df: pd.DataFrame | None = None,
    factor_frames: Mapping[str, pd.DataFrame] | None = None,
) -> dict[str, int | bool | str]:
    factor_frames = factor_frames or {}
    factor_files_expected = len(factor_frames)
    factor_files_with_rows = sum(0 if frame.empty else 1 for frame in factor_frames.values())
    factor_files_missing = max(0, factor_files_expected - factor_files_with_rows)
    has_municipal_votes = not municipal_df.empty
    has_national_votes = False if national_df is None else not national_df.empty
    status = classify_public_data_state(
        has_municipal_votes=has_municipal_votes,
        factor_files_expected=factor_files_expected,
        factor_files_with_rows=factor_files_with_rows,
    )
    return {
        "status": status,
        "has_municipal_votes": has_municipal_votes,
        "has_national_votes": has_national_votes,
        "factor_files_expected": factor_files_expected,
        "factor_files_with_rows": factor_files_with_rows,
        "factor_files_missing": factor_files_missing,
    }


def describe_public_data_state(country_label: str, state: Mapping[str, int | bool | str]) -> str:
    status = str(state["status"])
    if status == "missing_election_data":
        return f"The {country_label} adapter is configured, but no public election data files were found."
    if status == "missing_factor_data":
        return f"The {country_label} adapter has election data, but no public factor files with rows were found yet."
    if status == "partial_factor_data":
        return (
            f"The {country_label} adapter has election data, but only "
            f"{state['factor_files_with_rows']} of {state['factor_files_expected']} public factor files currently contain rows."
        )
    return f"The {country_label} adapter has public election data and factor files in place."
