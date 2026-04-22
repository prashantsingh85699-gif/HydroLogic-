"""
UtilityGuard — ReasoningAgent

Uses Gemini (with chain-of-thought) to classify sensor anomalies.
Falls back to rule-based logic if Gemini is unavailable.
"""

import json
import traceback
from typing import List

import google.generativeai as genai

from config import settings
from logger_setup import get_agent_logger
from models import IssueType, PerceptionOutput, ReasoningOutput, Severity

logger = get_agent_logger("ReasoningAgent")

# ── Mistral setup ───────────────────────────────────────────────────────────────

import requests

SYSTEM_PROMPT = """You are a water-utility anomaly classifier. You will receive sensor data for a zone and must classify it.

Rules:
- LEAK: pressure drop > 20% OR sudden flow anomaly (flow increase > 30%)
- SHORTAGE: consumption spike > 30% with roughly stable pressure (pressure change < 10%)
- NORMAL: otherwise

You MUST respond with ONLY a valid JSON object (no markdown fences, no extra text):
{
  "issue_type": "LEAK" | "SHORTAGE" | "NORMAL",
  "severity": "low" | "medium" | "high",
  "affected_zone": "<zone_id>",
  "confidence": <float 0-1>,
  "recommended_action": "<action string>",
  "reasoning_steps": ["step1", "step2", ...]
}

Severity guide:
- high: pressure drop > 35% or consumption spike > 50%
- medium: pressure drop 20-35% or consumption spike 30-50%
- low: minor anomalies or normal

Think step-by-step before answering. Include your reasoning steps in the JSON."""


class ReasoningAgent:
    """Classifies zone data as LEAK / SHORTAGE / NORMAL."""

    def run(self, perceptions: List[PerceptionOutput]) -> List[ReasoningOutput]:
        logger.info(f"🧠 ReasoningAgent cycle started — {len(perceptions)} zones")
        results: List[ReasoningOutput] = []

        for p in perceptions:
            try:
                result = self._classify_with_mistral(p)
            except Exception as e:
                logger.warning(f"Mistral failed for {p.zone_id}: {e}. Using rule-based fallback.")
                result = self._classify_rule_based(p)

            results.append(result)
            logger.info(
                f"Zone {p.zone_id}: {result.issue_type.value} "
                f"(severity={result.severity.value}, confidence={result.confidence:.2f})"
            )

        logger.info(f"✅ ReasoningAgent completed — {len(results)} classifications")
        return results

    # ── Mistral-powered classification ──────────────────────────────────────

    def _classify_with_mistral(self, p: PerceptionOutput) -> ReasoningOutput:
        if not settings.MISTRAL_API_KEY:
            raise RuntimeError("MISTRAL_API_KEY not configured")

        user_msg = (
            f"Zone: {p.zone_id}\n"
            f"Pressure: {p.pressure_psi:.2f} psi (change: {p.pressure_change_pct:+.2%})\n"
            f"Flow rate: {p.flow_rate_lps:.2f} lps (change: {p.flow_change_pct:+.2%})\n"
            f"Consumption: {p.consumption_m3:.2f} m³ (change: {p.consumption_change_pct:+.2%})"
        )

        headers = {
            "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "model": settings.MISTRAL_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        resp = requests.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        data = json.loads(raw)
        return ReasoningOutput(**data)

    # ── Rule-based fallback ────────────────────────────────────────────────

    def _classify_rule_based(self, p: PerceptionOutput) -> ReasoningOutput:
        steps = []
        issue = IssueType.NORMAL
        severity = Severity.LOW
        confidence = 0.9
        action = "No action required"

        steps.append(f"Pressure change: {p.pressure_change_pct:+.2%}")
        steps.append(f"Flow change: {p.flow_change_pct:+.2%}")
        steps.append(f"Consumption change: {p.consumption_change_pct:+.2%}")

        # LEAK detection
        if p.pressure_change_pct < -settings.PRESSURE_DROP_THRESHOLD:
            issue = IssueType.LEAK
            steps.append(f"Pressure drop {p.pressure_change_pct:+.2%} exceeds -{settings.PRESSURE_DROP_THRESHOLD:.0%} threshold → LEAK")
            if p.pressure_change_pct < -0.35:
                severity = Severity.HIGH
                confidence = 0.95
            else:
                severity = Severity.MEDIUM
                confidence = 0.85
            action = "Close valve and dispatch repair crew"

        elif p.flow_change_pct > 0.30:
            issue = IssueType.LEAK
            steps.append(f"Flow spike {p.flow_change_pct:+.2%} indicates possible pipe burst → LEAK")
            severity = Severity.MEDIUM
            confidence = 0.80
            action = "Inspect pipeline and close valve if confirmed"

        # SHORTAGE detection
        elif (p.consumption_change_pct > settings.CONSUMPTION_SPIKE_THRESHOLD
              and abs(p.pressure_change_pct) < 0.10):
            issue = IssueType.SHORTAGE
            steps.append(
                f"Consumption spike {p.consumption_change_pct:+.2%} with stable pressure → SHORTAGE"
            )
            if p.consumption_change_pct > 0.50:
                severity = Severity.HIGH
                confidence = 0.90
            else:
                severity = Severity.MEDIUM
                confidence = 0.80
            action = "Reroute resources from adjacent zones and alert consumers"

        else:
            steps.append("All values within normal range → NORMAL")

        return ReasoningOutput(
            issue_type=issue,
            severity=severity,
            affected_zone=p.zone_id,
            confidence=confidence,
            recommended_action=action,
            reasoning_steps=steps,
        )
