"""Ingest and replay control API."""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..config import settings
from ..ingest.runtime import runtime
from ..schemas.ingest import IngestStatus, ReplayLoadRequest, ReplaySource, ReplaySourcesResponse, ReplayStartRequest, ReplayStatus

router = APIRouter(tags=["ingest"])


def safe_source_path(source_type: str, source_path: str) -> Path:
    root = Path(settings.data_root).resolve()
    candidate = Path(source_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    candidate = candidate.resolve()
    allowed_suffix = ".jsonl" if source_type == "jsonl" else ".pcap"
    if root not in candidate.parents and candidate != root:
        raise HTTPException(status_code=400, detail="Source path must remain inside DATA_ROOT")
    if candidate.suffix.lower() != allowed_suffix:
        raise HTTPException(status_code=400, detail=f"Expected {allowed_suffix} source")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Replay source does not exist")
    if candidate.stat().st_size > settings.replay_max_file_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Replay source exceeds configured size limit")
    return candidate


@router.get("/api/ingest/status", response_model=IngestStatus)
def ingest_status() -> IngestStatus:
    return runtime.status()


@router.get("/api/ingest/metrics")
def ingest_metrics():
    return runtime.status().metrics


@router.get("/api/replay/status", response_model=ReplayStatus)
def replay_status() -> ReplayStatus:
    return runtime.controller.status()


@router.get("/api/replay/sources", response_model=ReplaySourcesResponse)
def replay_sources() -> ReplaySourcesResponse:
    root = Path(settings.data_root).resolve()
    sources: list[ReplaySource] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".pcap", ".jsonl"}:
            source_type = "pcap" if path.suffix.lower() == ".pcap" else "jsonl"
            sources.append(ReplaySource(name=path.name, source_type=source_type, size_bytes=path.stat().st_size, path=str(path.relative_to(root))))
    return ReplaySourcesResponse(sources=sources)


@router.post("/api/replay/load", response_model=ReplayStatus)
def replay_load(request: ReplayLoadRequest) -> ReplayStatus:
    path = safe_source_path(request.source_type, request.source_path)
    runtime.controller.source = runtime.controller.source if runtime.controller.status().state in {"RUNNING", "PAUSED"} else None
    runtime.controller.status_value.source_name = path.name
    runtime.controller.status_value.source_type = request.source_type
    return runtime.controller.status()


@router.post("/api/replay/start", response_model=ReplayStatus)
async def replay_start(request: ReplayStartRequest) -> ReplayStatus:
    if request.speed_multiplier > settings.replay_max_speed:
        raise HTTPException(status_code=422, detail="Replay speed exceeds configured maximum")
    path = safe_source_path(request.source_type, request.source_path)
    try:
        return await runtime.start(request.source_type, path, request.mode, request.speed_multiplier, request.target_flows_per_sec)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/api/replay/pause", response_model=ReplayStatus)
async def replay_pause() -> ReplayStatus:
    try:
        return await runtime.controller.pause()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/api/replay/resume", response_model=ReplayStatus)
async def replay_resume() -> ReplayStatus:
    try:
        return await runtime.controller.resume()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/api/replay/stop", response_model=ReplayStatus)
async def replay_stop() -> ReplayStatus:
    return await runtime.stop()


@router.post("/api/replay/restart", response_model=ReplayStatus)
async def replay_restart() -> ReplayStatus:
    try:
        return await runtime.controller.restart()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
