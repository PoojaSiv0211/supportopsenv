from typing import Dict, List
from uuid import uuid4

from app.models import Difficulty, TaskDefinition, Ticket
from app.graders import step_reward  # ✅ IMPORTANT


TASKS: List[TaskDefinition] = [

    TaskDefinition(
        task_id="easy_password_reset",
        difficulty=Difficulty.EASY,
        name="Password reset triage",
        customer_goal="Regain access safely",
        max_steps=6,
        grader=step_reward,  # ✅ FUNCTION (NOT STRING)
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
                "reset_link_or_unlock_path",
            ],
            "must_avoid": ["share_password"],
            "escalation_required": False,
        },
    ),

    TaskDefinition(
        task_id="medium_billing_dispute",
        difficulty=Difficulty.MEDIUM,
        name="Billing dispute",
        customer_goal="Resolve duplicate charge",
        max_steps=7,
        grader=step_reward,
        initial_ticket=Ticket(
            ticket_id="SUP-2001",
            title="Charged twice",
            customer_name="Marcus Lee",
            customer_tier="pro",
            product="SupportOps Analytics",
            issue_category="billing",
            description="I was charged twice for the same subscription.",
            sentiment="angry",
            risk_flags=["billing"],
            metadata={},
        ),
        hidden_truth={
            "required_facts": [
                "collect_charge_dates",
                "confirm_last_four",
                "check_duplicate_transaction",
            ],
            "must_avoid": ["request_full_card_number"],
            "escalation_required": False,
        },
    ),

    TaskDefinition(
        task_id="hard_security_breach",
        difficulty=Difficulty.HARD,
        name="Security breach",
        customer_goal="Contain breach safely",
        max_steps=8,
        grader=step_reward,
        initial_ticket=Ticket(
            ticket_id="SUP-3001",
            title="Unknown export",
            customer_name="Priya Narayanan",
            customer_tier="enterprise",
            product="SupportOps Admin Console",
            issue_category="security_incident",
            description="Large export triggered from admin account.",
            sentiment="urgent",
            risk_flags=["security"],
            metadata={},
        ),
        hidden_truth={
            "required_facts": [
                "treat_as_security_incident",
                "preserve_logs",
                "revoke_or_rotate_sessions",
                "escalate_to_security",
            ],
            "must_avoid": ["share_password"],
            "escalation_required": True,
        },
    ),
]


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