"""
UtilityGuard — Mock IoT sensor data generator.

Generates realistic water-utility sensor readings for 5 zones.
Supports injecting LEAK and SHORTAGE anomalies.
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional

from config import settings
from models import SensorReading

# ── Baseline values per zone ───────────────────────────────────────────────────

ZONE_BASELINES: Dict[str, dict] = {
    "zone_1": {"pressure_psi": 55.0, "flow_rate_lps": 12.0, "consumption_m3": 320.0},
    "zone_2": {"pressure_psi": 52.0, "flow_rate_lps": 10.5, "consumption_m3": 280.0},
    "zone_3": {"pressure_psi": 58.0, "flow_rate_lps": 14.0, "consumption_m3": 350.0},
    "zone_4": {"pressure_psi": 50.0, "flow_rate_lps": 9.0,  "consumption_m3": 260.0},
    "zone_5": {"pressure_psi": 54.0, "flow_rate_lps": 11.0, "consumption_m3": 300.0},
}

# Active anomaly injections: zone_id -> "leak" | "shortage"
_active_anomalies: Dict[str, str] = {}


def inject_leak(zone_id: str) -> None:
    """Inject a LEAK anomaly into a zone (pressure drop + flow spike)."""
    _active_anomalies[zone_id] = "leak"


def inject_shortage(zone_id: str) -> None:
    """Inject a SHORTAGE anomaly into a zone (consumption spike, stable pressure)."""
    _active_anomalies[zone_id] = "shortage"


def clear_anomalies() -> None:
    """Remove all injected anomalies."""
    _active_anomalies.clear()


def clear_anomaly(zone_id: str) -> None:
    """Remove anomaly for a specific zone."""
    _active_anomalies.pop(zone_id, None)


def _jitter(value: float, pct: float = 0.03) -> float:
    """Add small random variation."""
    return value * (1 + random.uniform(-pct, pct))


def generate_readings() -> List[SensorReading]:
    """Generate one set of readings for all zones, applying any active anomalies."""
    readings: List[SensorReading] = []
    now = datetime.utcnow().isoformat()

    for zone_id, baseline in ZONE_BASELINES.items():
        pressure = _jitter(baseline["pressure_psi"])
        flow = _jitter(baseline["flow_rate_lps"])
        consumption = _jitter(baseline["consumption_m3"])

        anomaly = _active_anomalies.get(zone_id)

        if anomaly == "leak":
            # Pressure drops 25-40%, flow spikes 50-80%
            pressure *= random.uniform(0.55, 0.75)
            flow *= random.uniform(1.5, 1.8)

        elif anomaly == "shortage":
            # Consumption spikes 35-60%, pressure stays roughly stable
            consumption *= random.uniform(1.35, 1.6)
            pressure *= random.uniform(0.97, 1.03)

        readings.append(SensorReading(
            zone_id=zone_id,
            timestamp=now,
            pressure_psi=round(pressure, 2),
            flow_rate_lps=round(flow, 2),
            consumption_m3=round(consumption, 2),
        ))

    # Persist to file
    _save_readings(readings)
    return readings


def _save_readings(readings: List[SensorReading]) -> None:
    """Save latest readings to the sensor JSON file."""
    data = [r.model_dump() for r in readings]
    os.makedirs(os.path.dirname(settings.SENSOR_FILE), exist_ok=True)
    with open(settings.SENSOR_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_last_readings() -> Optional[List[SensorReading]]:
    """Load the most recent saved readings from disk."""
    if not os.path.exists(settings.SENSOR_FILE):
        return None
    with open(settings.SENSOR_FILE, "r") as f:
        data = json.load(f)
    return [SensorReading(**d) for d in data]
