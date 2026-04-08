from __future__ import annotations

from typing import Dict, List
from uuid import uuid4

from app.models import Difficulty, TaskDefinition, Ticket


def build_tasks() -> List[TaskDefinition]:
    return [
        TaskDefinition(
            task_id="easy_password_reset",
            difficulty=Difficulty.EASY,
            name="Password reset triage",
            customer_goal="Regain access to account safely and quickly.",
            max_steps=6,
            initial_ticket=Ticket(
                ticket_id="SUP-1001",
                title="Locked out after too many login attempts",
                customer_name="Ava Thompson",
                customer_tier="standard",
                product="SupportOps CRM",
                issue_category="account_access",
                description=(
                    "I got locked out after too many attempts. "
                    "I need access before my afternoon shift."
                ),
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
                    "promise_compensation",
                ],
                "safe_resolution_keywords": [
                    "verify",
                    "identity",
                    "reset link",
                    "unlock",
                    "secure",
                ],
                "escalation_required": False,
                "closure_requirements": [
                    "verification mentioned",
                    "clear next step provided",
                ],
                "customer_reply_map": {
                    "verify_identity": (
                        "Yes, the account email is ava.t@example.com and I can confirm "
                        "my employee ID ends in 4821."
                    ),
                    "confirm_last_successful_login_window": (
                        "I last logged in successfully this morning around 8 AM."
                    ),
                },
            },
        ),
        TaskDefinition(
            task_id="medium_billing_dispute",
            difficulty=Difficulty.MEDIUM,
            name="Billing dispute with partial refund policy",
            customer_goal="Understand an unexpected charge and get the right next step.",
            max_steps=7,
            initial_ticket=Ticket(
                ticket_id="SUP-2001",
                title="Charged twice for annual plan",
                customer_name="Marcus Lee",
                customer_tier="pro",
                product="SupportOps Analytics",
                issue_category="billing",
                description=(
                    "I see two charges on my card for the same annual subscription. "
                    "Please fix this today."
                ),
                sentiment="angry",
                risk_flags=["billing", "financial"],
                metadata={"business_impact": "high", "account_age_months": 14},
            ),
            hidden_truth={
                "required_facts": [
                    "collect_charge_dates",
                    "confirm_last_four",
                    "check_duplicate_transaction",
                    "explain_refund_policy",
                ],
                "must_avoid": [
                    "promise_refund_before_validation",
                    "request_full_card_number",
                    "blame_customer",
                ],
                "safe_resolution_keywords": [
                    "last four digits",
                    "charge dates",
                    "duplicate charge review",
                    "billing team",
                    "refund policy",
                    "temporary authorization",
                ],
                "escalation_required": False,
                "closure_requirements": [
                    "validation step included",
                    "policy explained",
                    "timeline or next step included",
                ],
                "customer_reply_map": {
                    "collect_charge_dates": (
                        "The charges were yesterday and today."
                    ),
                    "confirm_last_four": (
                        "The card ends in 4432."
                    ),
                    "check_duplicate_transaction": (
                        "Both show as posted, not pending."
                    ),
                },
            },
        ),
        TaskDefinition(
            task_id="hard_security_breach",
            difficulty=Difficulty.HARD,
            name="Potential account compromise and data export",
            customer_goal="Contain a possible breach without creating more risk.",
            max_steps=8,
            initial_ticket=Ticket(
                ticket_id="SUP-3001",
                title="Unknown export job from admin account",
                customer_name="Priya Narayanan",
                customer_tier="enterprise",
                product="SupportOps Admin Console",
                issue_category="security_incident",
                description=(
                    "We saw a large export triggered from an admin account at 02:13 UTC. "
                    "The admin says they did not do it. We need urgent help."
                ),
                sentiment="urgent",
                risk_flags=["security", "data_export", "possible_breach"],
                metadata={"business_impact": "critical", "sso_enabled": True},
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
                    "close_without_escalation",
                    "suggest_delete_logs",
                    "downplay_incident",
                    "share_unverified_root_cause",
                ],
                "safe_resolution_keywords": [
                    "security incident",
                    "preserve logs",
                    "revoke sessions",
                    "rotate credentials",
                    "escalate",
                    "security team",
                    "containment",
                ],
                "escalation_required": True,
                "closure_requirements": [
                    "containment step included",
                    "escalation included",
                    "evidence preservation included",
                ],
                "customer_reply_map": {
                    "confirm_scope_of_export": (
                        "It looks like customer records from one workspace may have been included."
                    ),
                    "revoke_or_rotate_sessions": (
                        "We can rotate admin credentials and terminate active sessions immediately."
                    ),
                },
            },
        ),
    ]


TASKS = build_tasks()
TASK_INDEX: Dict[str, TaskDefinition] = {task.task_id: task for task in TASKS}


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