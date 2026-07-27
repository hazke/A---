"""Helpers for building perception metrics and quality summaries."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, List, Optional

from core.perception.schemas import (
    DataQualitySummary,
    FieldStatus,
    NullableMetric,
    QualityFlag,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ok_metric(
    value: float,
    *,
    unit: Optional[str] = None,
    as_of: Optional[datetime] = None,
) -> NullableMetric:
    return NullableMetric(
        value=float(value),
        status=FieldStatus.OK,
        unit=unit,
        as_of=as_of,
    )


def missing_metric(*, message: str = "not available") -> NullableMetric:
    return NullableMetric(status=FieldStatus.MISSING)


def degraded_metric(
    value: Optional[float],
    *,
    unit: Optional[str] = None,
    as_of: Optional[datetime] = None,
) -> NullableMetric:
    return NullableMetric(
        value=float(value) if value is not None else None,
        status=FieldStatus.DEGRADED,
        unit=unit,
        as_of=as_of,
    )


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()
            if value in {"", "-", "--", "nan", "None"}:
                return None
        result = float(value)
        if result != result:  # NaN
            return None
        return result
    except (TypeError, ValueError):
        return None


def pick_row(df, code_col: str, target_code: str):
    if df is None or df.empty:
        return None
    normalized = target_code.replace(".SH", "").replace(".SZ", "").strip()
    series = df[code_col].astype(str).str.replace(r"\.(SH|SZ)$", "", regex=True)
    matches = df[series == normalized]
    if matches.empty:
        matches = df[df[code_col].astype(str).str.contains(normalized, na=False)]
    if matches.empty:
        return None
    return matches.iloc[0]


def summarize_quality(
    flags: Iterable[QualityFlag],
    *,
    freshness_sla_seconds: int,
) -> DataQualitySummary:
    flag_list = list(flags)
    if not flag_list:
        overall = FieldStatus.OK
    else:
        priority = {
            FieldStatus.MISSING: 4,
            FieldStatus.STALE: 3,
            FieldStatus.DEGRADED: 2,
            FieldStatus.OK: 1,
        }
        overall = max(flag_list, key=lambda f: priority[f.status]).status

    critical = {FieldStatus.MISSING, FieldStatus.STALE}
    passed = all(flag.status not in critical for flag in flag_list)

    return DataQualitySummary(
        overall_status=overall,
        freshness_sla_seconds=freshness_sla_seconds,
        flags=flag_list,
        passed=passed,
    )


def flag(
    field_path: str,
    status: FieldStatus,
    *,
    message: Optional[str] = None,
    source: Optional[str] = None,
    observed_at: Optional[datetime] = None,
) -> QualityFlag:
    return QualityFlag(
        field_path=field_path,
        status=status,
        message=message,
        source=source,
        observed_at=observed_at,
    )
