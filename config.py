"""
UtilityGuard — Central configuration loaded from environment / .env file.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # AI Model
    MISTRAL_API_KEY: str = field(default_factory=lambda: os.getenv("MISTRAL_API_KEY", ""))
    MISTRAL_MODEL: str = "mistral-small-latest"

    # Notification
    SENDGRID_API_KEY: str = field(default_factory=lambda: os.getenv("SENDGRID_API_KEY", ""))
    SLACK_WEBHOOK_URL: str = field(default_factory=lambda: os.getenv("SLACK_WEBHOOK_URL", ""))
    NOTIFICATION_EMAIL: str = field(default_factory=lambda: os.getenv("NOTIFICATION_EMAIL", "vendor@utility.com"))

    # Paths
    DATA_DIR: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data"))
    SENSOR_FILE: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data", "sensors.json"))
    MEMORY_FILE: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data", "memory.json"))
    CRM_FILE: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data", "crm.json"))
    LOG_FILE: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data", "utilityguard.log"))

    # Thresholds
    PRESSURE_DROP_THRESHOLD: float = 0.20  # 20%
    CONSUMPTION_SPIKE_THRESHOLD: float = 0.30  # 30%

    # Polling
    POLL_INTERVAL_SECONDS: int = 60

    def __post_init__(self):
        os.makedirs(self.DATA_DIR, exist_ok=True)


settings = Settings()
