"""
UtilityGuard — ActionAgent

Executes corrective actions: closes valves, reroutes resources,
and writes to a mock CRM (local JSON file).
"""

import json
import os
from datetime import datetime
from typing import List

from config import settings
from logger_setup import get_agent_logger
from models import ActionResult, ActionType, IssueType, ReasoningOutput

logger = get_agent_logger("ActionAgent")


class ActionAgent:
    """Executes corrective actions based on reasoning output."""

    def run(self, reasonings: List[ReasoningOutput]) -> List[ActionResult]:
        logger.info(f"⚡ ActionAgent cycle started — {len(reasonings)} classifications")
        results: List[ActionResult] = []

        for r in reasonings:
            if r.issue_type == IssueType.NORMAL:
                results.append(ActionResult(
                    zone_id=r.affected_zone,
                    action_type=ActionType.NO_ACTION,
                    success=True,
                    details="Zone operating normally — no action needed",
                ))
                continue

            try:
                if r.issue_type == IssueType.LEAK:
                    result = self._close_valve(r)
                elif r.issue_type == IssueType.SHORTAGE:
                    result = self._reroute_resources(r)
                else:
                    result = ActionResult(
                        zone_id=r.affected_zone,
                        action_type=ActionType.NO_ACTION,
                        success=True,
                        details="Unknown issue type — logged for review",
                    )
                results.append(result)
            except Exception as e:
                logger.error(f"Action failed for {r.affected_zone}: {e}")
                results.append(ActionResult(
                    zone_id=r.affected_zone,
                    action_type=ActionType.NO_ACTION,
                    success=False,
                    details=f"Action failed: {str(e)}",
                ))

        logger.info(f"✅ ActionAgent completed — {len(results)} actions")
        return results

    def _close_valve(self, r: ReasoningOutput) -> ActionResult:
        """Simulate closing a valve and update mock CRM."""
        logger.info(f"🔧 Closing valve for zone {r.affected_zone}")
        self._write_crm_entry(r.affected_zone, "valve_closed", r)
        self._mock_api_call("close_valve", r.affected_zone)

        return ActionResult(
            zone_id=r.affected_zone,
            action_type=ActionType.VALVE_CLOSED,
            success=True,
            details=f"Valve closed for {r.affected_zone} due to {r.issue_type.value} "
                    f"(severity: {r.severity.value})",
        )

    def _reroute_resources(self, r: ReasoningOutput) -> ActionResult:
        """Simulate rerouting resources from adjacent zones."""
        logger.info(f"🔄 Rerouting resources to zone {r.affected_zone}")
        self._write_crm_entry(r.affected_zone, "resource_rerouted", r)
        self._mock_api_call("reroute_resources", r.affected_zone)

        return ActionResult(
            zone_id=r.affected_zone,
            action_type=ActionType.RESOURCE_REROUTED,
            success=True,
            details=f"Resources rerouted to {r.affected_zone} due to {r.issue_type.value} "
                    f"(severity: {r.severity.value})",
        )

    def _write_crm_entry(self, zone_id: str, action: str, r: ReasoningOutput) -> None:
        """Write an entry to the mock CRM JSON file."""
        crm_path = settings.CRM_FILE
        os.makedirs(os.path.dirname(crm_path), exist_ok=True)

        entries = []
        if os.path.exists(crm_path):
            try:
                with open(crm_path, "r") as f:
                    entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                entries = []

        entries.append({
            "zone_id": zone_id,
            "action": action,
            "issue_type": r.issue_type.value,
            "severity": r.severity.value,
            "recommended_action": r.recommended_action,
            "timestamp": datetime.utcnow().isoformat(),
        })

        with open(crm_path, "w") as f:
            json.dump(entries, f, indent=2)

        logger.debug(f"CRM entry written: {action} for {zone_id}")

    def _mock_api_call(self, endpoint: str, zone_id: str) -> None:
        """Simulate an external API call (just logs it)."""
        logger.info(f"📡 Mock API call: POST /api/{endpoint} — zone={zone_id} → 200 OK")
