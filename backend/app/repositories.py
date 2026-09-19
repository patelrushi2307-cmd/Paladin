"""SQLite persistence boundary for alerts."""
from __future__ import annotations
from contextlib import contextmanager

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any
from .schemas.alert import Alert


class AlertRepository:
    def __init__(self, database_url: str = "sqlite:///./data/paladin.db") -> None:
        self.database_path = self._path_from_url(database_url)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._conn = sqlite3.connect(self.database_path, check_same_thread=False)
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        self.initialize()

    @staticmethod
    def _path_from_url(database_url: str) -> Path:
        return Path(database_url.removeprefix("sqlite:///"))

    @contextmanager
    def _connection(self):
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.close()
            except Exception:
                pass

    def initialize(self) -> None:
        with self._lock, self._connection() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS alerts (alert_id TEXT PRIMARY KEY, dedup_key TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, last_seen TEXT NOT NULL, payload TEXT NOT NULL)")
            columns = {row[1] for row in connection.execute("PRAGMA table_info(alerts)").fetchall()}
            for name, definition in (("dedup_key", "TEXT NOT NULL DEFAULT ''"), ("status", "TEXT NOT NULL DEFAULT 'NEW'"), ("created_at", "TEXT NOT NULL DEFAULT ''"), ("last_seen", "TEXT NOT NULL DEFAULT ''")):
                if name not in columns:
                    connection.execute(f"ALTER TABLE alerts ADD COLUMN {name} {definition}")
            connection.execute("UPDATE alerts SET dedup_key = alert_id WHERE dedup_key = ''")
            connection.execute("UPDATE alerts SET status = 'NEW' WHERE status = ''")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_alerts_dedup ON alerts(dedup_key, last_seen)")

    def create(self, alert: Alert, dedup_key: str) -> Alert:
        with self._lock, self._connection() as connection:
            connection.execute("INSERT OR REPLACE INTO alerts(alert_id, dedup_key, status, created_at, last_seen, payload) VALUES(?,?,?,?,?,?)", (alert.alert_id, dedup_key, alert.status, (alert.created_at or alert.timestamp).isoformat(), (alert.last_seen or alert.timestamp).isoformat(), alert.model_dump_json()))
        return alert

    def update(self, alert: Alert, dedup_key: str) -> Alert:
        return self.create(alert, dedup_key)


    def get(self, alert_id: str) -> Alert | None:
        with self._lock, self._connection() as connection:
            row = connection.execute("SELECT payload FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()
        return Alert.model_validate_json(row[0]) if row else None

    def find_recent_duplicate(self, dedup_key: str, since: datetime) -> Alert | None:
        with self._lock, self._connection() as connection:
            row = connection.execute("SELECT payload FROM alerts WHERE dedup_key = ? AND last_seen >= ? ORDER BY last_seen DESC LIMIT 1", (dedup_key, since.isoformat())).fetchone()
        return Alert.model_validate_json(row[0]) if row else None

    def list(self, *, limit: int = 100, offset: int = 0, threat_class: str | None = None, severity: str | None = None, status: str | None = None, source_ip: str | None = None, destination_ip: str | None = None) -> list[Alert]:
        clauses, params = [], []
        for field, value in (("threat_class", threat_class), ("severity", severity), ("status", status), ("source_ip", source_ip), ("destination_ip", destination_ip)):
            if value:
                clauses.append(f"json_extract(payload, '$.{field}') = ?"); params.append(value)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock, self._connection() as connection:
            rows = connection.execute(f"SELECT payload FROM alerts{where} ORDER BY last_seen DESC LIMIT ? OFFSET ?", (*params, min(limit, 500), max(offset, 0))).fetchall()
        return [Alert.model_validate_json(row[0]) for row in rows]

    def count(self) -> int:
        with self._lock, self._connection() as connection:
            return int(connection.execute("SELECT COUNT(*) FROM alerts").fetchone()[0])

    def list_alerts(self) -> list[dict[str, Any]]:
        return [item.model_dump(mode="json") for item in self.list()]

    def set_status(self, alert_id: str, status: str) -> Alert | None:
        alert = self.get(alert_id)
        if not alert: return None
        updated = alert.model_copy(update={"status": status})
        with self._lock, self._connection() as connection:
            connection.execute("UPDATE alerts SET status = ?, payload = ? WHERE alert_id = ?", (status, updated.model_dump_json(), alert_id))
        return updated


    def summary(self) -> dict[str, Any]:
        alerts = self.list(limit=500)
        by_threat: dict[str, int] = {}; by_severity: dict[str, int] = {}
        for alert in alerts:
            by_threat[alert.threat_class.value] = by_threat.get(alert.threat_class.value, 0) + 1
            by_severity[alert.severity.value] = by_severity.get(alert.severity.value, 0) + 1
        return {"total": len(alerts), "new": sum(item.status == "NEW" for item in alerts), "by_threat": by_threat, "by_severity": by_severity}
