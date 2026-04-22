"""
UtilityGuard — Pydantic data models shared across all agents.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────

class IssueType(str, Enum):
    LEAK = "LEAK"
    SHORTAGE = "SHORTAGE"
    NORMAL = "NORMAL"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionType(str, Enum):
    VALVE_CLOSED = "valve_closed"
    RESOURCE_REROUTED = "resource_rerouted"
    NO_ACTION = "no_action"


# ── Sensor ─────────────────────────────────────────────────────────────────────

class SensorReading(BaseModel):
    zone_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    pressure_psi: float
    flow_rate_lps: float
    consumption_m3: float


# ── Perception ─────────────────────────────────────────────────────────────────

class PerceptionOutput(BaseModel):
    zone_id: str
    timestamp: str
    pressure_psi: float
    flow_rate_lps: float
    consumption_m3: float
    pressure_change_pct: float = 0.0
    flow_change_pct: float = 0.0
    consumption_change_pct: float = 0.0


# ── Reasoning ──────────────────────────────────────────────────────────────────

class ReasoningOutput(BaseModel):
    issue_type: IssueType
    severity: Severity
    affected_zone: str
    confidence: float = Field(ge=0, le=1)
    recommended_action: str
    reasoning_steps: List[str]


# ── Action ─────────────────────────────────────────────────────────────────────

class ActionResult(BaseModel):
    zone_id: str
    action_type: ActionType
    success: bool
    details: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ── Notification ───────────────────────────────────────────────────────────────

class NotificationResult(BaseModel):
    channel: str  # "email", "slack", "log"
    success: bool
    details: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ── Agent Log Entry ────────────────────────────────────────────────────────────

class AgentLogEntry(BaseModel):
    agent: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    message: str
    data: Optional[dict] = None


# ── Cycle Summary ──────────────────────────────────────────────────────────────

class CycleSummary(BaseModel):
    cycle_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    perceptions: List[PerceptionOutput]
    reasonings: List[ReasoningOutput]
    actions: List[ActionResult]
    notifications: List[NotificationResult]
    status: str = "completed"
