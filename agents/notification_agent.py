"""
UtilityGuard — NotificationAgent

Sends real notifications via:
  1. SendGrid email (primary)
  2. Slack webhook (fallback)
  3. Log-only (final fallback)
"""

import json
import requests
from typing import List

from config import settings
from logger_setup import get_agent_logger
from models import ActionResult, NotificationResult, ReasoningOutput

logger = get_agent_logger("NotificationAgent")


class NotificationAgent:
    """Sends notifications through available channels with fallback logic."""

    def run(
        self,
        reasonings: List[ReasoningOutput],
        actions: List[ActionResult],
    ) -> List[NotificationResult]:
        logger.info(f"📨 NotificationAgent cycle started")
        results: List[NotificationResult] = []

        # Only notify for non-NORMAL issues
        alerts = [
            (r, a) for r, a in zip(reasonings, actions)
            if r.issue_type.value != "NORMAL"
        ]

        if not alerts:
            logger.info("No anomalies detected — no notifications needed")
            return results

        for reasoning, action in alerts:
            subject = (
                f"🚨 UtilityGuard Alert: {reasoning.issue_type.value} "
                f"in {reasoning.affected_zone}"
            )
            body = self._format_message(reasoning, action)
            result = self._send_notification(subject, body)
            results.append(result)

        logger.info(f"✅ NotificationAgent completed — {len(results)} notifications sent")
        return results

    def _format_message(self, r: ReasoningOutput, a: ActionResult) -> str:
        return (
            f"Issue Type: {r.issue_type.value}\n"
            f"Severity: {r.severity.value}\n"
            f"Affected Zone: {r.affected_zone}\n"
            f"Confidence: {r.confidence:.0%}\n"
            f"Recommended Action: {r.recommended_action}\n"
            f"\nReasoning:\n" + "\n".join(f"  • {s}" for s in r.reasoning_steps) +
            f"\n\nAction Taken: {a.action_type.value}\n"
            f"Action Details: {a.details}\n"
            f"Action Success: {'✅' if a.success else '❌'}"
        )

    def _send_notification(self, subject: str, body: str) -> NotificationResult:
        """Try email → slack → log-only."""

        # 1. Try SendGrid email
        if settings.SENDGRID_API_KEY:
            try:
                result = self._send_email(subject, body)
                if result.success:
                    return result
                logger.warning("Email failed, trying Slack fallback")
            except Exception as e:
                logger.warning(f"Email error: {e}, trying Slack fallback")

        # 2. Try Slack webhook
        if settings.SLACK_WEBHOOK_URL:
            try:
                result = self._send_slack(subject, body)
                if result.success:
                    return result
                logger.warning("Slack failed, falling back to log-only")
            except Exception as e:
                logger.warning(f"Slack error: {e}, falling back to log-only")

        # 3. Final fallback: log only
        return self._log_notification(subject, body)

    def _send_email(self, subject: str, body: str) -> NotificationResult:
        """Send email via SendGrid API."""
        logger.info(f"📧 Sending email: {subject}")

        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": settings.NOTIFICATION_EMAIL}]}],
                "from": {"email": "utilityguard@alerts.com", "name": "UtilityGuard"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            },
            timeout=10,
        )

        success = resp.status_code in (200, 202)
        detail = f"SendGrid response: {resp.status_code}"
        if success:
            logger.info(f"✅ Email sent to {settings.NOTIFICATION_EMAIL}")
        else:
            logger.warning(f"Email failed: {resp.status_code} {resp.text[:200]}")

        return NotificationResult(channel="email", success=success, details=detail)

    def _send_slack(self, subject: str, body: str) -> NotificationResult:
        """Send message via Slack incoming webhook."""
        logger.info(f"💬 Sending Slack message: {subject}")

        payload = {
            "text": f"*{subject}*\n```\n{body}\n```",
        }

        resp = requests.post(
            settings.SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )

        success = resp.status_code == 200
        detail = f"Slack response: {resp.status_code}"
        if success:
            logger.info("✅ Slack notification sent")
        else:
            logger.warning(f"Slack failed: {resp.status_code}")

        return NotificationResult(channel="slack", success=success, details=detail)

    def _log_notification(self, subject: str, body: str) -> NotificationResult:
        """Fallback: just log the notification."""
        logger.info(f"📋 LOG-ONLY notification:\n  Subject: {subject}\n  Body:\n{body}")
        return NotificationResult(
            channel="log",
            success=True,
            details="Notification logged (no email/Slack configured)",
        )
