"""Dependency providers shared by API routes."""

from .config import Settings, settings
from .repositories import AlertRepository
from .alerts.service import AlertService


_alert_repository = AlertRepository()
_alert_service = AlertService(_alert_repository)


def get_settings() -> Settings:
    return settings


def get_alert_repository() -> AlertRepository:
    return _alert_repository


def get_alert_service() -> AlertService:
    return _alert_service
