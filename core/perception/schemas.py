"""
AgenticQ Stage 01 — Data Perception contracts.

Missing fields are never coerced to zero; each metric carries an explicit status.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class FieldStatus(str, Enum):
    OK = "ok"
    MISSING = "missing"
    STALE = "stale"
    DEGRADED = "degraded"


class QualityFlag(BaseModel):
    field_path: str = Field(..., description="Dot-path to the affected field")
    status: FieldStatus
    message: Optional[str] = None
    source: Optional[str] = None
    observed_at: Optional[datetime] = None


class NullableMetric(BaseModel):
    """A scalar observation. value is None when status is not OK."""
    value: Optional[float] = None
    status: FieldStatus = FieldStatus.MISSING
    unit: Optional[str] = None
    as_of: Optional[datetime] = None


class MarketData(BaseModel):
    symbol: str
    name: Optional[str] = None
    last_price: NullableMetric = Field(default_factory=NullableMetric)
    open: NullableMetric = Field(default_factory=NullableMetric)
    high: NullableMetric = Field(default_factory=NullableMetric)
    low: NullableMetric = Field(default_factory=NullableMetric)
    prev_close: NullableMetric = Field(default_factory=NullableMetric)
    change_pct: NullableMetric = Field(default_factory=NullableMetric)
    volume: NullableMetric = Field(default_factory=NullableMetric)
    amount: NullableMetric = Field(default_factory=NullableMetric)
    vwap: NullableMetric = Field(default_factory=NullableMetric)
    bid_ask_spread: NullableMetric = Field(default_factory=NullableMetric)
    turnover_rate: NullableMetric = Field(default_factory=NullableMetric)
    as_of: Optional[datetime] = None


class CapitalFlowBucket(BaseModel):
    net_inflow: NullableMetric = Field(default_factory=NullableMetric)


class CapitalFlowData(BaseModel):
    main: CapitalFlowBucket = Field(default_factory=CapitalFlowBucket)
    super_large: CapitalFlowBucket = Field(default_factory=CapitalFlowBucket)
    large: CapitalFlowBucket = Field(default_factory=CapitalFlowBucket)
    medium: CapitalFlowBucket = Field(default_factory=CapitalFlowBucket)
    small: CapitalFlowBucket = Field(default_factory=CapitalFlowBucket)
    as_of: Optional[datetime] = None


class SectorItem(BaseModel):
    code: str
    name: str
    change_pct: NullableMetric = Field(default_factory=NullableMetric)


class SectorThemeData(BaseModel):
    sectors: List[SectorItem] = Field(default_factory=list)
    etfs: List[SectorItem] = Field(default_factory=list)
    as_of: Optional[datetime] = None


class GlobalTicker(BaseModel):
    symbol: str
    name: str
    last_price: NullableMetric = Field(default_factory=NullableMetric)
    change_pct: NullableMetric = Field(default_factory=NullableMetric)


class GlobalContextData(BaseModel):
    tickers: List[GlobalTicker] = Field(default_factory=list)
    as_of: Optional[datetime] = None


class DataQualitySummary(BaseModel):
    overall_status: FieldStatus = FieldStatus.MISSING
    freshness_sla_seconds: int = 120
    flags: List[QualityFlag] = Field(default_factory=list)
    passed: bool = False


class LivePerception(BaseModel):
    symbol: str
    collected_at: datetime
    market: MarketData
    capital_flow: CapitalFlowData
    sector_theme: SectorThemeData
    global_context: GlobalContextData
    quality: DataQualitySummary


class FrozenSnapshot(LivePerception):
    snapshot_id: str = Field(default_factory=lambda: str(uuid4()))
    frozen_at: datetime
    is_frozen: bool = True


class FreezeSnapshotRequest(BaseModel):
    symbol: str = Field(default="601138", description="Target symbol")


class FreezeSnapshotResponse(BaseModel):
    snapshot: FrozenSnapshot
