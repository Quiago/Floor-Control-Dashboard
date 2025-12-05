# app/models/__init__.py
"""Data models for workflow builder."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class WorkflowStatus(Enum):
    """Workflow status options."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ActionType(Enum):
    """Supported action types."""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SYSTEM_ALERT = "alert"


@dataclass
class SensorReading:
    """A single sensor reading."""
    equipment_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ThresholdConfig:
    """Configuration for threshold-based triggers."""
    sensor_type: str
    operator: str  # >, <, >=, <=, ==, between
    threshold: float
    threshold_max: Optional[float] = None
    unit: str = ""


@dataclass
class ActionConfig:
    """Configuration for action nodes."""
    action_type: ActionType
    recipient: str  # phone, email, or webhook URL
    severity: AlertSeverity = AlertSeverity.WARNING
    message_template: Optional[str] = None


@dataclass
class WorkflowNode:
    """A node in the workflow."""
    id: str
    node_type: str
    label: str
    category: str
    position: Dict[str, float]
    is_action: bool = False
    configured: bool = False
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """An edge connecting two nodes."""
    id: str
    source: str
    target: str
    animated: bool = True


@dataclass
class Workflow:
    """Complete workflow definition."""
    id: str
    name: str
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.DRAFT
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class AlertLog:
    """Log entry for an alert."""
    id: int
    workflow_id: str
    action_type: str
    recipient: str
    message: str
    status: str
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Result of a workflow execution."""
    workflow_id: str
    execution_id: int
    triggered_by: str
    trigger_data: Dict[str, Any]
    actions_executed: int
    success: bool
    results: List[Dict[str, Any]] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


__all__ = [
    'WorkflowStatus', 'AlertSeverity', 'ActionType',
    'SensorReading', 'ThresholdConfig', 'ActionConfig',
    'WorkflowNode', 'WorkflowEdge', 'Workflow',
    'AlertLog', 'ExecutionResult'
]
