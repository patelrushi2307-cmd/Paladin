"""Line-by-line normalized flow source."""

import json
import logging
from collections.abc import AsyncIterator
from pathlib import Path
from ..schemas.flow import FlowEvent
from .base import TrafficSource

logger = logging.getLogger("paladin.ingest")


class JsonlTrafficSource(TrafficSource):
    source_type = "jsonl"

    def __init__(self, path: Path) -> None:
        self.path = path
        self.malformed = 0
        self._stopped = False

    async def start(self) -> None:
        self._stopped = False

    async def stop(self) -> None:
        self._stopped = True

    async def stream(self) -> AsyncIterator[FlowEvent]:
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if self._stopped:
                    return
                if not line.strip():
                    continue
                try:
                    yield FlowEvent.model_validate(json.loads(line))
                except (json.JSONDecodeError, ValueError, TypeError) as exc:
                    self.malformed += 1
                    logger.warning("[INGEST] MALFORMED_EVENT line=%s error=%s", line_number, exc)

    def health(self) -> dict[str, str]:
        return {"status": "stopped" if self._stopped else "ready", "source": str(self.path)}
