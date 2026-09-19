"""Central environment configuration."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/paladin.db")
    frontend_port: int = int(os.getenv("FRONTEND_PORT", "5173"))
    replay_default_rate: int = int(os.getenv("REPLAY_DEFAULT_RATE", "100"))
    replay_max_rate: int = int(os.getenv("REPLAY_MAX_RATE", "5000"))
    data_root: str = os.getenv("DATA_ROOT", "./data" if os.path.isdir("./data") else "../data")
    pcap_root: str = os.getenv("PCAP_ROOT", "./data/raw" if os.path.isdir("./data/raw") else "../data/raw")
    jsonl_root: str = os.getenv("JSONL_ROOT", "./data/raw" if os.path.isdir("./data/raw") else "../data/raw")
    event_queue_maxsize: int = int(os.getenv("EVENT_QUEUE_MAXSIZE", "10000"))
    flow_idle_timeout_seconds: float = float(os.getenv("FLOW_IDLE_TIMEOUT_SECONDS", "30"))
    flow_max_duration_seconds: float = float(os.getenv("FLOW_MAX_DURATION_SECONDS", "300"))
    replay_default_speed: float = float(os.getenv("REPLAY_DEFAULT_SPEED", "1"))
    replay_max_speed: float = float(os.getenv("REPLAY_MAX_SPEED", "100"))
    replay_max_file_mb: int = int(os.getenv("REPLAY_MAX_FILE_MB", "2048"))
    metrics_window_seconds: int = int(os.getenv("METRICS_WINDOW_SECONDS", "5"))
    detection_window_seconds: int = int(os.getenv("DETECTION_WINDOW_SECONDS", "5"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    display_mask_ips: bool = os.getenv("DISPLAY_MASK_IPS", "true").lower() == "true"
    display_raw_dns_names: bool = os.getenv("DISPLAY_RAW_DNS_NAMES", "false").lower() == "true"


settings = Settings()
