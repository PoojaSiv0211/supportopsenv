from __future__ import annotations

from typing import Dict, List
from uuid import uuid4

from app.models import Difficulty, TaskDefinition, Ticket


# =============================
# STATIC TASK DEFINITIONS (IMPORTANT)
# =============================
TASKS: List[TaskDefinition] = [
    # -------------------------
    # EASY TASK
    # -------------------------
    TaskDefinition(
        task_id="easy_password_reset",
        difficulty=Difficulty.EASY,
        name="Password reset triage",
        customer_goal="Regain access safely",
        max_steps=6,
        initial_ticket=Ticket(
            ticket_id="SUP-1001",
            title="Locked out",
            customer_name="Ava Thompson",
            customer_tier="standard",
            product="SupportOps CRM",
            issue_category="account_access",
            description="I got locked out after too many attempts.",
            sentiment="frustrated",
            risk_flags=["account_access"],
            metadata={"business_impact": "moderate"},
        ),
        hidden_truth={
            "required_facts": [
                "verify_identity",
                "confirm_last_successful_login_window",
                "reset_link_or_unlock_path",
            ],
            "must_avoid": [
                "share_password",
                "disable_security_without_verification",
            ],
            "safe_resolution_keywords": [
                "verify",
                "identity",
                "reset link",
                "secure",
            ],
            "escalation_required": False,
        },
    ),

    # -------------------------
    # MEDIUM TASK
    # -------------------------
    TaskDefinition(
        task_id="medium_billing_dispute",
        difficulty=Difficulty.MEDIUM,
        name="Billing dispute",
        customer_goal="Resolve duplicate charge",
        max_steps=7,
        initial_ticket=Ticket(
            ticket_id="SUP-2001",
            title="Charged twice",
            customer_name="Marcus Lee",
            customer_tier="pro",
            product="SupportOps Analytics",
            issue_category="billing",
            description="I was charged twice for the same subscription.",
            sentiment="angry",
            risk_flags=["billing", "financial"],
            metadata={"business_impact": "high"},
        ),
        hidden_truth={
            "required_facts": [
                "collect_charge_dates",
                "confirm_last_four",
                "check_duplicate_transaction",
                "explain_refund_policy",
            ],
            "must_avoid": [
                "request_full_card_number",
                "promise_refund_before_validation",
            ],
            "safe_resolution_keywords": [
                "charge dates",
                "last four digits",
                "duplicate",
                "refund policy",
            ],
            "escalation_required": False,
        },
    ),

    # -------------------------
    # HARD TASK
    # -------------------------
    TaskDefinition(
        task_id="hard_security_breach",
        difficulty=Difficulty.HARD,
        name="Security breach",
        customer_goal="Contain breach safely",
        max_steps=8,
        initial_ticket=Ticket(
            ticket_id="SUP-3001",
            title="Unknown export",
            customer_name="Priya Narayanan",
            customer_tier="enterprise",
            product="SupportOps Admin Console",
            issue_category="security_incident",
            description="Large export triggered from admin account.",
            sentiment="urgent",
            risk_flags=["security", "data_export"],
            metadata={"business_impact": "critical"},
        ),
        hidden_truth={
            "required_facts": [
                "treat_as_security_incident",
                "preserve_logs",
                "revoke_or_rotate_sessions",
                "confirm_scope_of_export",
                "escalate_to_security",
            ],
            "must_avoid": [
                "share_password",
                "downplay_incident",
                "close_without_escalation",
            ],
            "safe_resolution_keywords": [
                "security incident",
                "preserve logs",
                "revoke sessions",
                "rotate credentials",
                "escalate",
            ],
            "escalation_required": True,
        },
    ),
]


# =============================
# INDEX + HELPERS
# =============================
TASK_INDEX: Dict[str, TaskDefinition] = {
    task.task_id: task for task in TASKS
}


def get_task_by_id(task_id: str) -> TaskDefinition:
    if task_id not in TASK_INDEX:
        raise KeyError(f"Unknown task_id: {task_id}")
    return TASK_INDEX[task_id]


def get_task_by_difficulty(difficulty: Difficulty) -> TaskDefinition:
    for task in TASKS:
        if task.difficulty == difficulty:
            return task
    raise KeyError(f"No task found for difficulty: {difficulty}")


def new_episode_id() -> str:
    return str(uuid4())