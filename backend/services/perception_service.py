"""Business logic for AgenticQ data perception."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from core.perception.schemas import (
    FreezeSnapshotResponse,
    FrozenSnapshot,
    LivePerception,
)
from core.perception.ingestor import PerceptionIngestor
from core.perception.snapshot_store import SnapshotStore


class PerceptionService:
    def __init__(self):
        self.ingestor = PerceptionIngestor()
        self.store = SnapshotStore()

    def get_live(self, symbol: Optional[str] = None) -> LivePerception:
        return self.ingestor.collect(symbol)

    def freeze_snapshot(self, symbol: Optional[str] = None) -> FreezeSnapshotResponse:
        live = self.ingestor.collect(symbol)
        snapshot = FrozenSnapshot(
            **live.model_dump(),
            snapshot_id=str(uuid4()),
            frozen_at=datetime.now(timezone.utc),
            is_frozen=True,
        )
        saved = self.store.save(snapshot)
        return FreezeSnapshotResponse(snapshot=saved)

    def get_latest_snapshot(self, symbol: str) -> Optional[FrozenSnapshot]:
        return self.store.get_latest(symbol)

    def get_snapshot(self, snapshot_id: str) -> Optional[FrozenSnapshot]:
        return self.store.get_by_id(snapshot_id)

    def list_snapshots(self, symbol: str, limit: int = 20) -> List[FrozenSnapshot]:
        return self.store.list_snapshots(symbol, limit=limit)
