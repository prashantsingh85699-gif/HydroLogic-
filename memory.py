"""
UtilityGuard — Persistent memory store (JSON-file backed).

Stores event history, agent state, and action logs across runs.
"""

import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import settings


class PersistentMemory:
    """Thread-safe, JSON-file-backed memory for all agents."""

    def __init__(self, filepath: Optional[str] = None):
        self._filepath = filepath or settings.MEMORY_FILE
        self._lock = threading.Lock()
        self._data: Dict[str, Any] = self._load()

    # ── Public API ─────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value
            self._save()

    def append_event(self, event: dict) -> None:
        """Append an event to the event history list."""
        with self._lock:
            events = self._data.setdefault("events", [])
            event.setdefault("timestamp", datetime.utcnow().isoformat())
            events.append(event)
            # Keep last 500 events
            if len(events) > 500:
                self._data["events"] = events[-500:]
            self._save()

    def get_events(self, limit: int = 50) -> List[dict]:
        with self._lock:
            events = self._data.get("events", [])
            return events[-limit:]

    def get_zone_history(self, zone_id: str, limit: int = 20) -> List[dict]:
        """Get recent events for a specific zone."""
        with self._lock:
            events = self._data.get("events", [])
            zone_events = [e for e in events if e.get("zone_id") == zone_id]
            return zone_events[-limit:]

    def store_baseline(self, zone_id: str, reading: dict) -> None:
        """Store the latest 'normal' reading as baseline for comparison."""
        with self._lock:
            baselines = self._data.setdefault("baselines", {})
            baselines[zone_id] = reading
            self._save()

    def get_baseline(self, zone_id: str) -> Optional[dict]:
        with self._lock:
            return self._data.get("baselines", {}).get(zone_id)

    def store_cycle_summary(self, summary: dict) -> None:
        """Store a complete cycle summary."""
        with self._lock:
            summaries = self._data.setdefault("cycle_summaries", [])
            summaries.append(summary)
            if len(summaries) > 100:
                self._data["cycle_summaries"] = summaries[-100:]
            self._save()

    def get_cycle_summaries(self, limit: int = 20) -> List[dict]:
        with self._lock:
            return self._data.get("cycle_summaries", [])[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._data = {}
            self._save()

    # ── Internal ───────────────────────────────────────────────────────────

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        with open(self._filepath, "w") as f:
            json.dump(self._data, f, indent=2, default=str)


# Singleton instance
memory = PersistentMemory()
