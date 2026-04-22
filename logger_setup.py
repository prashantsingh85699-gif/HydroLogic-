"""
UtilityGuard — Logging setup with in-memory ring buffer for dashboard display.
"""

import logging
import os
import threading
from collections import deque
from datetime import datetime
from typing import List

from config import settings


class LogRecord:
    """Lightweight log entry for the dashboard."""
    __slots__ = ("timestamp", "agent", "level", "message")

    def __init__(self, timestamp: str, agent: str, level: str, message: str):
        self.timestamp = timestamp
        self.agent = agent
        self.level = level
        self.message = message

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "agent": self.agent,
            "level": self.level,
            "message": self.message,
        }


class InMemoryHandler(logging.Handler):
    """Logging handler that stores records in a thread-safe ring buffer."""

    def __init__(self, maxlen: int = 500):
        super().__init__()
        self._buffer: deque = deque(maxlen=maxlen)
        self._lock_rw = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        entry = LogRecord(
            timestamp=datetime.utcnow().isoformat(),
            agent=getattr(record, "agent_name", record.name),
            level=record.levelname,
            message=self.format(record),
        )
        with self._lock_rw:
            self._buffer.append(entry)

    def get_logs(self, limit: int = 100) -> List[dict]:
        with self._lock_rw:
            items = list(self._buffer)[-limit:]
        return [r.to_dict() for r in items]

    def clear(self) -> None:
        with self._lock_rw:
            self._buffer.clear()


# ── Singleton handler ──────────────────────────────────────────────────────────
_memory_handler = InMemoryHandler(maxlen=500)
_memory_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

# File handler
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
_file_handler = logging.FileHandler(settings.LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))


def get_agent_logger(agent_name: str) -> logging.Logger:
    """Get a named logger that writes to both file and in-memory buffer."""
    logger = logging.getLogger(f"utilityguard.{agent_name}")
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_memory_handler)
        logger.addHandler(_file_handler)
        # Prevent propagation to root
        logger.propagate = False
    return logger


def get_dashboard_logs(limit: int = 100) -> List[dict]:
    """Retrieve recent logs for the Streamlit dashboard by reading from disk."""
    if not os.path.exists(settings.LOG_FILE):
        return []
    
    logs = []
    try:
        with open(settings.LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                parts = line.split("] utilityguard.", 1)
                if len(parts) == 2:
                    ts_level = parts[0].split(" [")
                    if len(ts_level) == 2:
                        ts = ts_level[0].strip()
                        level = ts_level[1].strip()
                        agent_msg = parts[1].split(":", 1)
                        if len(agent_msg) == 2:
                            agent = agent_msg[0].strip()
                            msg = agent_msg[1].strip()
                            logs.append({
                                "timestamp": ts,
                                "agent": agent,
                                "level": level,
                                "message": msg
                            })
    except Exception:
        pass
    return logs


def clear_logs() -> None:
    _memory_handler.clear()
