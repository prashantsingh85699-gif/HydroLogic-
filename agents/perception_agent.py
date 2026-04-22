"""
UtilityGuard — PerceptionAgent

Monitors mock IoT sensor data, computes deltas vs. baseline,
and outputs structured PerceptionOutput JSON.
"""

from typing import List

from logger_setup import get_agent_logger
from memory import memory
from models import PerceptionOutput, SensorReading
from sensor_data import generate_readings, ZONE_BASELINES

logger = get_agent_logger("PerceptionAgent")


class PerceptionAgent:
    """Polls mock IoT sensors and computes change percentages."""

    def run(self, readings: List[SensorReading] | None = None) -> List[PerceptionOutput]:
        """
        Generate or accept sensor readings, compare against baseline,
        and return enriched PerceptionOutput list.
        """
        logger.info("🔍 PerceptionAgent cycle started")

        if readings is None:
            readings = generate_readings()
            logger.info(f"Generated readings for {len(readings)} zones")

        outputs: List[PerceptionOutput] = []

        for reading in readings:
            baseline = memory.get_baseline(reading.zone_id)
            if baseline is None:
                # Use static defaults as initial baseline
                bl = ZONE_BASELINES.get(reading.zone_id, {
                    "pressure_psi": reading.pressure_psi,
                    "flow_rate_lps": reading.flow_rate_lps,
                    "consumption_m3": reading.consumption_m3,
                })
            else:
                bl = baseline

            # Compute percentage changes
            def pct_change(current: float, base: float) -> float:
                if base == 0:
                    return 0.0
                return round((current - base) / base, 4)

            p_change = pct_change(reading.pressure_psi, bl["pressure_psi"])
            f_change = pct_change(reading.flow_rate_lps, bl["flow_rate_lps"])
            c_change = pct_change(reading.consumption_m3, bl["consumption_m3"])

            output = PerceptionOutput(
                zone_id=reading.zone_id,
                timestamp=reading.timestamp,
                pressure_psi=reading.pressure_psi,
                flow_rate_lps=reading.flow_rate_lps,
                consumption_m3=reading.consumption_m3,
                pressure_change_pct=p_change,
                flow_change_pct=f_change,
                consumption_change_pct=c_change,
            )
            outputs.append(output)

            # Update baseline for NORMAL readings only (no large deviation)
            if abs(p_change) < 0.10 and abs(f_change) < 0.10 and abs(c_change) < 0.10:
                memory.store_baseline(reading.zone_id, {
                    "pressure_psi": reading.pressure_psi,
                    "flow_rate_lps": reading.flow_rate_lps,
                    "consumption_m3": reading.consumption_m3,
                })

            logger.debug(
                f"Zone {reading.zone_id}: P={reading.pressure_psi:.1f} psi "
                f"(Δ{p_change:+.1%}), F={reading.flow_rate_lps:.1f} lps "
                f"(Δ{f_change:+.1%}), C={reading.consumption_m3:.1f} m³ "
                f"(Δ{c_change:+.1%})"
            )

        logger.info(f"✅ PerceptionAgent completed — {len(outputs)} zone outputs")
        return outputs
