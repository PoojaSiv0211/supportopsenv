from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ActionType(str, Enum):
    ANALYZE = "analyze"
    ASK_CUSTOMER = "ask_customer"
    INTERNAL_NOTE = "internal_note"
    PROPOSE_RESOLUTION = "propose_resolution"
    ESCALATE = "escalate"
    CLOSE_CASE = "close_case"


class Message(BaseModel):
    role: Literal["system", "customer", "agent", "internal"]
    content: str


class Ticket(BaseModel):
    ticket_id: str
    title: str
    customer_name: str
    customer_tier: str
    product: str
    issue_category: str
    description: str
    sentiment: str
    risk_flags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskDefinition(BaseModel):
    task_id: str
    difficulty: Difficulty
    name: str
    customer_goal: str
    hidden_truth: Dict[str, Any]
    initial_ticket: Ticket
    max_steps: int = 8


class ResetRequest(BaseModel):
    difficulty: Optional[Difficulty] = None
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    action_type: ActionType
    content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Observation(BaseModel):
    episode_id: str
    task_id: str
    difficulty: Difficulty
    step_count: int
    max_steps: int
    remaining_steps: int
    done: bool
    latest_customer_message: str
    ticket: Ticket
    history: List[Message]
    guidance: str
    available_actions: List[ActionType]
    interim_score: float
    warnings: List[str] = Field(default_factory=list)


class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = Field(default_factory=dict)


class EnvironmentState(BaseModel):
    episode_id: str
    task: TaskDefinition
    history: List[Message] = Field(default_factory=list)
    step_count: int = 0
    done: bool = False
    cumulative_reward: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    gathered_facts: Dict[str, bool] = Field(default_factory=dict)
    duplicate_question_count: int = 0
    escalated: bool = False
    resolution_proposed: bool = False
    case_closed: bool = False
    asked_for_customer_info: List[str] = Field(default_factory=list)
    risk_mistakes: List[str] = Field(default_factory=list)
    trajectory: List[Dict[str, Any]] = Field(default_factory=list)