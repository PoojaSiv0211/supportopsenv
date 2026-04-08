from __future__ import annotations

from typing import Dict, List, Tuple

from app.models import ActionType, EnvironmentState, StepRequest, TaskDefinition


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _contains_any(text: str, keywords: List[str]) -> bool:
    t = _normalize(text)
    return any(k.lower() in t for k in keywords)


def extract_fact_hits(task: TaskDefinition, action: StepRequest) -> Dict[str, bool]:
    text = _normalize(action.content)
    fact_hits = {fact: False for fact in task.hidden_truth["required_facts"]}

    mapping = {
        "verify_identity": ["verify", "identity", "employee id", "confirm email"],
        "confirm_last_successful_login_window": ["last login", "last successful login"],
        "reset_link_or_unlock_path": ["reset link", "unlock", "password reset"],

        "collect_charge_dates": ["charge date", "when were you charged"],
        "confirm_last_four": ["last four", "card ends"],
        "check_duplicate_transaction": ["duplicate charge", "posted", "pending"],
        "explain_refund_policy": ["refund policy", "billing review"],

        "treat_as_security_incident": ["security incident", "breach"],
        "preserve_logs": ["preserve logs", "retain logs"],
        "revoke_or_rotate_sessions": ["revoke session", "terminate sessions", "rotate credentials"],
        "confirm_scope_of_export": ["scope", "what was exported"],
        "escalate_to_security": ["escalate", "security team"],
    }

    for fact, phrases in mapping.items():
        if fact in fact_hits and any(p in text for p in phrases):
            fact_hits[fact] = True

    return fact_hits


def step_reward(
    state: EnvironmentState, action: StepRequest
) -> Tuple[float, List[str], Dict[str, float]]:

    task = state.task
    text = _normalize(action.content)
    warnings: List[str] = []

    components = {
        "base_action": 0.0,
        "progress": 0.0,
        "clarity": 0.0,
        "risk_penalty": 0.0,
        "efficiency_penalty": 0.0,
    }

    # Base reward
    if len(text) >= 15:
        components["base_action"] += 0.05
    else:
        components["efficiency_penalty"] -= 0.05
        warnings.append("Action too short")

    if action.action_type == ActionType.ANALYZE:
        components["base_action"] += 0.03
    elif action.action_type == ActionType.ASK_CUSTOMER:
        components["base_action"] += 0.04
    elif action.action_type == ActionType.PROPOSE_RESOLUTION:
        components["base_action"] += 0.05
    elif action.action_type == ActionType.ESCALATE:
        components["base_action"] += 0.06

    # Progress
    fact_hits = extract_fact_hits(task, action)
    for fact, hit in fact_hits.items():
        if hit and not state.gathered_facts.get(fact, False):
            state.gathered_facts[fact] = True
            components["progress"] += 0.14

    # Good communication
    if _contains_any(text, ["please", "thank you", "help"]):
        components["clarity"] += 0.03

    # Duplicate question penalty
    if action.action_type == ActionType.ASK_CUSTOMER:
        if text in state.asked_for_customer_info:
            components["efficiency_penalty"] -= 0.1
            warnings.append("Duplicate question")
        else:
            state.asked_for_customer_info.append(text)

    # Risk penalties
    risky_patterns = {
        "share_password": ["password"],
        "request_full_card_number": ["full card", "cvv"],
        "downplay_incident": ["not serious"],
    }

    for risk_name in task.hidden_truth["must_avoid"]:
        phrases = risky_patterns.get(risk_name, [])
        if any(p in text for p in phrases):
            components["risk_penalty"] -= 0.3
            state.risk_mistakes.append(risk_name)
            warnings.append(f"Risk: {risk_name}")

    # Escalation
    if action.action_type == ActionType.ESCALATE:
        state.escalated = True

    # Resolution tracking
    if action.action_type == ActionType.PROPOSE_RESOLUTION:
        state.resolution_proposed = True

    if action.action_type == ActionType.CLOSE_CASE:
        state.case_closed = True

    reward = round(sum(components.values()), 4)
    reward = max(-1.0, min(1.0, reward))

    return reward, warnings, components


def final_grade(state: EnvironmentState) -> Dict[str, float]:
    task = state.task

    total_required = len(task.hidden_truth["required_facts"])
    facts_collected = sum(state.gathered_facts.values())
    completion = facts_collected / max(1, total_required)

    safety = 1.0 - min(1.0, 0.25 * len(state.risk_mistakes))

    escalation = 1.0
    if task.hidden_truth.get("escalation_required", False):
        escalation = 1.0 if state.escalated else 0.0

    resolution = 1.0 if state.resolution_proposed else 0.3
    efficiency = max(0.0, 1.0 - 0.1 * state.duplicate_question_count)

    score = (
        0.4 * completion
        + 0.3 * safety
        + 0.2 * escalation
        + 0.1 * efficiency
    )

    score = max(0.0, min(1.0, score))

    return {
        "score": round(score, 4),
        "completion": round(completion, 4),
        "safety": round(safety, 4),
        "escalation": round(escalation, 4),
        "resolution": round(resolution, 4),
        "efficiency": round(efficiency, 4),
    }