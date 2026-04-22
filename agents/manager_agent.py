"""
UtilityGuard — ManagerAgent (Orchestrator)

Receives reasoning output, plans multi-step response,
delegates to ActionAgent and NotificationAgent.
Implements self-correction with retry + channel fallback.
"""

from typing import List, Tuple

from logger_setup import get_agent_logger
from memory import memory
from models import (
    ActionResult,
    CycleSummary,
    IssueType,
    NotificationResult,
    PerceptionOutput,
    ReasoningOutput,
)
from agents.action_agent import ActionAgent
from agents.notification_agent import NotificationAgent

logger = get_agent_logger("ManagerAgent")

MAX_RETRIES = 2


class ManagerAgent:
    """Orchestrates multi-step response with self-correction."""

    def __init__(self):
        self.action_agent = ActionAgent()
        self.notification_agent = NotificationAgent()

    def run(
        self,
        perceptions: List[PerceptionOutput],
        reasonings: List[ReasoningOutput],
        cycle_id: str,
    ) -> CycleSummary:
        logger.info(f"🎯 ManagerAgent orchestrating cycle {cycle_id}")

        # ── Step 1: Plan response ──────────────────────────────────────────
        anomalies = [r for r in reasonings if r.issue_type != IssueType.NORMAL]
        logger.info(
            f"Plan: {len(anomalies)} anomalies detected out of {len(reasonings)} zones"
        )

        if anomalies:
            for a in anomalies:
                logger.info(
                    f"  → {a.affected_zone}: {a.issue_type.value} "
                    f"({a.severity.value}, confidence={a.confidence:.2f})"
                )

        # ── Step 2: Execute actions with retry ─────────────────────────────
        action_results = self._execute_with_retry(
            task_name="Actions",
            func=lambda: self.action_agent.run(reasonings),
            fallback=lambda: self._fallback_actions(reasonings),
        )

        # ── Step 3: Send notifications with retry ─────────────────────────
        notification_results = self._execute_with_retry(
            task_name="Notifications",
            func=lambda: self.notification_agent.run(reasonings, action_results),
            fallback=lambda: self._fallback_notifications(reasonings, action_results),
        )

        # ── Step 4: Build summary ──────────────────────────────────────────
        summary = CycleSummary(
            cycle_id=cycle_id,
            perceptions=perceptions,
            reasonings=reasonings,
            actions=action_results,
            notifications=notification_results,
            status="completed",
        )

        # Persist events
        for r, a in zip(reasonings, action_results):
            if r.issue_type != IssueType.NORMAL:
                memory.append_event({
                    "cycle_id": cycle_id,
                    "zone_id": r.affected_zone,
                    "issue_type": r.issue_type.value,
                    "severity": r.severity.value,
                    "confidence": r.confidence,
                    "action": a.action_type.value,
                    "action_success": a.success,
                    "action_details": a.details,
                })

        memory.store_cycle_summary(summary.model_dump())
        logger.info(f"✅ ManagerAgent cycle {cycle_id} completed")
        return summary

    def _execute_with_retry(self, task_name, func, fallback, max_retries=MAX_RETRIES):
        """Execute a task with retry and fallback logic."""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                if attempt == 0:
                    result = func()
                else:
                    logger.warning(
                        f"⚠️ {task_name}: retry #{attempt} with fallback"
                    )
                    result = fallback()
                return result

            except Exception as e:
                last_error = e
                logger.error(
                    f"❌ {task_name}: attempt {attempt + 1}/{max_retries + 1} "
                    f"failed — {e}"
                )

        # All retries exhausted
        logger.error(
            f"🚫 {task_name}: all {max_retries + 1} attempts failed. "
            f"Last error: {last_error}"
        )
        return []

    def _fallback_actions(self, reasonings: List[ReasoningOutput]) -> List[ActionResult]:
        """Minimal fallback if ActionAgent crashes: log-only actions."""
        logger.warning("Using fallback action handler (log-only)")
        results = []
        for r in reasonings:
            results.append(ActionResult(
                zone_id=r.affected_zone,
                action_type="no_action",
                success=False,
                details="Fallback: action logged but not executed",
            ))
        return results

    def _fallback_notifications(
        self,
        reasonings: List[ReasoningOutput],
        actions: List[ActionResult],
    ) -> List[NotificationResult]:
        """Minimal fallback notification (log only)."""
        logger.warning("Using fallback notification handler (log-only)")
        results = []
        for r, a in zip(reasonings, actions):
            if r.issue_type != IssueType.NORMAL:
                logger.info(
                    f"📋 FALLBACK ALERT: {r.issue_type.value} in {r.affected_zone} "
                    f"| action={a.action_type} | severity={r.severity.value}"
                )
                results.append(NotificationResult(
                    channel="log",
                    success=True,
                    details="Fallback log-only notification",
                ))
        return results
