"""Persist frozen perception snapshots as JSON files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from core.perception.schemas import FrozenSnapshot


class SnapshotStore:
    def __init__(self, base_dir: Optional[Path] = None):
        project_root = Path(__file__).resolve().parents[2]
        self.base_dir = base_dir or project_root / "data" / "snapshots"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _symbol_dir(self, symbol: str) -> Path:
        path = self.base_dir / symbol
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, snapshot: FrozenSnapshot) -> FrozenSnapshot:
        symbol_dir = self._symbol_dir(snapshot.symbol)
        file_path = symbol_dir / f"{snapshot.snapshot_id}.json"
        payload = snapshot.model_dump(mode="json")
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        latest_path = symbol_dir / "latest.json"
        latest_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return snapshot

    def get_latest(self, symbol: str) -> Optional[FrozenSnapshot]:
        latest_path = self._symbol_dir(symbol) / "latest.json"
        if not latest_path.exists():
            return None
        data = json.loads(latest_path.read_text(encoding="utf-8"))
        return FrozenSnapshot.model_validate(data)

    def get_by_id(self, snapshot_id: str) -> Optional[FrozenSnapshot]:
        for file_path in self.base_dir.rglob(f"{snapshot_id}.json"):
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return FrozenSnapshot.model_validate(data)
        return None

    def list_snapshots(self, symbol: str, limit: int = 20) -> List[FrozenSnapshot]:
        symbol_dir = self._symbol_dir(symbol)
        files = sorted(
            symbol_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        snapshots: List[FrozenSnapshot] = []
        for file_path in files:
            if file_path.name == "latest.json":
                continue
            data = json.loads(file_path.read_text(encoding="utf-8"))
            snapshots.append(FrozenSnapshot.model_validate(data))
            if len(snapshots) >= limit:
                break
        return snapshots
