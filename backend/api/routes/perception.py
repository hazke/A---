"""AgenticQ Stage 01 — data perception API routes."""
from fastapi import APIRouter, HTTPException, status

from backend.models.perception_schemas import (
    FreezeSnapshotRequest,
    FreezeSnapshotResponse,
    FrozenSnapshot,
    LivePerception,
)
from backend.services.perception_service import PerceptionService

router = APIRouter()


def get_perception_service() -> PerceptionService:
    if not hasattr(get_perception_service, "_instance"):
        get_perception_service._instance = PerceptionService()
    return get_perception_service._instance


@router.get("/perception/live", response_model=LivePerception)
async def get_live_perception(symbol: str = "601138"):
    """Collect current (non-frozen) perception data for a symbol."""
    try:
        service = get_perception_service()
        return service.get_live(symbol)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post("/perception/snapshots/freeze", response_model=FreezeSnapshotResponse)
async def freeze_snapshot(request: FreezeSnapshotRequest):
    """Capture an immutable frozen snapshot from the current live feed."""
    try:
        service = get_perception_service()
        return service.freeze_snapshot(request.symbol)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.get("/perception/snapshots/latest", response_model=FrozenSnapshot)
async def get_latest_snapshot(symbol: str = "601138"):
    """Return the most recently frozen snapshot for a symbol."""
    service = get_perception_service()
    snapshot = service.get_latest_snapshot(symbol)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No frozen snapshot found for symbol {symbol}",
        )
    return snapshot


@router.get("/perception/snapshots/{snapshot_id}", response_model=FrozenSnapshot)
async def get_snapshot(snapshot_id: str):
    """Return a frozen snapshot by ID."""
    service = get_perception_service()
    snapshot = service.get_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found",
        )
    return snapshot
