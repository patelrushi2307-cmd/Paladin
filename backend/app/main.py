"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import alerts, detectors, features, health, ingest, models, system
from .config import settings
from .dependencies import get_alert_repository
from .realtime.websocket import router as websocket_router

logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("paladin.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_alert_repository().initialize()
    logger.info("[API] receive-only service initialized")
    yield


app = FastAPI(
    title="Paladin API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(system.router)
app.include_router(alerts.router)
app.include_router(ingest.router)
app.include_router(features.router)
app.include_router(detectors.router)
app.include_router(models.router)
app.include_router(websocket_router)
