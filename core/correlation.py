import logging
import math
import numbers


logger = logging.getLogger(__name__)


def _log_invalid_result(level: int, factor: str, party: str, year: int, r, n: int, mode: str, reason: str) -> None:
    logger.log(
        level,
        "Invalid correlation result | factor=%s party=%s year=%s r=%r n=%s mode=%s reason=%s",
        factor,
        party,
        year,
        r,
        n,
        mode,
        reason,
    )


def invalid_result_log_level(mode: str) -> int:
    return logging.DEBUG if str(mode).startswith("precompute") else logging.WARNING


def is_valid_correlation(r) -> bool:
    if r is None:
        return False
    if not isinstance(r, numbers.Real):
        return False
    r = float(r)
    if not math.isfinite(r):
        return False
    return -1.0 <= r <= 1.0


def correlation_band(r: float) -> str | None:
    if not is_valid_correlation(r):
        return None
    abs_r = abs(float(r))
    if abs_r >= 0.70:
        return "strong"
    if abs_r >= 0.50:
        return "moderate"
    if abs_r >= 0.30:
        return "weak"
    return "none"


def corr_strength_label(r) -> str:
    if not is_valid_correlation(r):
        return "Unavailable"
    r = float(r)
    a = abs(r)
    direction = "↑" if r > 0 else "↓"
    if a >= 0.70:
        return f"{direction} Strong ({r:.2f})"
    if a >= 0.50:
        return f"{direction} Moderate ({r:.2f})"
    if a >= 0.30:
        return f"{direction} Weak ({r:.2f})"
    return f"None ({r:.2f})"


def compute_correlation_result(merged, *, factor: str, party: str, year: int, mode: str) -> dict:
    cleaned = merged.dropna(subset=["share", "metric"]).copy()
    n = len(cleaned)
    log_level = invalid_result_log_level(mode)

    if n < 10:
        _log_invalid_result(log_level, factor, party, year, None, n, mode, "insufficient_rows")
        return {"merged": cleaned, "r": None, "valid": False, "n": n, "reason": "insufficient_rows"}

    if cleaned["share"].nunique(dropna=True) < 2:
        _log_invalid_result(log_level, factor, party, year, None, n, mode, "zero_variance_share")
        return {"merged": cleaned, "r": None, "valid": False, "n": n, "reason": "zero_variance_share"}

    if cleaned["metric"].nunique(dropna=True) < 2:
        _log_invalid_result(log_level, factor, party, year, None, n, mode, "zero_variance_metric")
        return {"merged": cleaned, "r": None, "valid": False, "n": n, "reason": "zero_variance_metric"}

    raw_r = cleaned["share"].corr(cleaned["metric"])
    if not is_valid_correlation(raw_r):
        _log_invalid_result(log_level, factor, party, year, raw_r, n, mode, "non_finite_or_out_of_range")
        return {"merged": cleaned, "r": raw_r, "valid": False, "n": n, "reason": "non_finite_or_out_of_range"}

    r = round(float(raw_r), 2)
    return {"merged": cleaned, "r": r, "valid": True, "n": n, "reason": None}
