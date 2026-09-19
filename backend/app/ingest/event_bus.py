"""Bounded in-process event bus with explicit overflow accounting."""

import asyncio
import logging
from ..schemas.flow import FlowEvent

logger = logging.getLogger("paladin.ingest")


class FlowEventBus:
    def __init__(self, maxsize: int = 10000) -> None:
        self.queue: asyncio.Queue[FlowEvent] = asyncio.Queue(maxsize=maxsize)
        self.maxsize = maxsize
        self.dropped = 0

    async def publish(self, event: FlowEvent, timeout: float = 1.0) -> bool:
        try:
            await asyncio.wait_for(self.queue.put(event), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self.dropped += 1
            logger.warning("[INGEST] QUEUE_OVERFLOW dropped=%s", self.dropped)
            return False

    async def consume(self) -> FlowEvent:
        return await self.queue.get()

    def task_done(self) -> None:
        self.queue.task_done()

    def status(self) -> dict[str, int]:
        return {"size": self.queue.qsize(), "maxsize": self.maxsize, "dropped": self.dropped}
