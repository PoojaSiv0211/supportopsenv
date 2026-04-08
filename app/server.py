from __future__ import annotations

from typing import Dict, List
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from uuid import uuid4

from app.graders import final_grade, step_reward
from app.models import (
    ActionType,
    Difficulty,
    EnvironmentState,
    Message,
    Observation,
    ResetRequest,
    StepRequest,
    StepResponse,
)
from app.tasks import TASKS, get_task_by_difficulty, get_task_by_id


app = FastAPI(
    title="SupportOpsEnv",
    version="2.0.0",
    description="Risk-aware AI customer support RL environment with explainable decision intelligence.",
)

CURRENT_STATE: EnvironmentState | None = None


def _bootstrap_history(task) -> List[Message]:
    return [
        Message(
            role="system",
            content=(
                "You are operating inside SupportOpsEnv. "
                "Your goal is to handle the ticket safely, efficiently, and correctly. "
                "Avoid risky actions and follow real-world support practices."
            ),
        ),
        Message(role="customer", content=task.initial_ticket.description),
    ]


def _customer_reply_for_action(state: EnvironmentState, action: StepRequest) -> str:
    text = action.content.lower()
    reply_map = state.task.hidden_truth.get("customer_reply_map", {})

    for fact, response in reply_map.items():
        if any(word in text for word in fact.split("_")):
            return response

    return "Understood. Please proceed with the safest steps."


def _build_observation(state: EnvironmentState) -> Observation:
    latest_customer_message = ""
    for msg in reversed(state.history):
        if msg.role == "customer":
            latest_customer_message = msg.content
            break

    grade = final_grade(state)

    return Observation(
        episode_id=state.episode_id,
        task_id=state.task.task_id,
        difficulty=state.task.difficulty,
        step_count=state.step_count,
        max_steps=state.task.max_steps,
        remaining_steps=max(0, state.task.max_steps - state.step_count),
        done=state.done,
        latest_customer_message=latest_customer_message,
        ticket=state.task.initial_ticket,
        history=state.history,
        guidance="Act safely, collect facts, avoid risky actions, escalate when needed.",
        available_actions=[
            ActionType.ANALYZE,
            ActionType.ASK_CUSTOMER,
            ActionType.INTERNAL_NOTE,
            ActionType.PROPOSE_RESOLUTION,
            ActionType.ESCALATE,
            ActionType.CLOSE_CASE,
        ],
        interim_score=grade["score"],
        warnings=state.warnings[-5:],
    )


def _create_state(task) -> EnvironmentState:
    return EnvironmentState(
        episode_id=str(uuid4()),
        task=task,
        history=_bootstrap_history(task),
        gathered_facts={fact: False for fact in task.hidden_truth["required_facts"]},
    )


def _ensure_initialized() -> EnvironmentState:
    global CURRENT_STATE
    if CURRENT_STATE is None:
        CURRENT_STATE = _create_state(TASKS[0])
    return CURRENT_STATE


@app.get("/")
def root():
    return {"status": "SupportOpsEnv running"}


@app.get("/health")
def health():
    return {"status": "healthy", "env": "SupportOpsEnv"}


@app.post("/reset", response_model=StepResponse)
def reset_env(request: ResetRequest = ResetRequest()):
    global CURRENT_STATE

    if request.task_id:
        task = get_task_by_id(request.task_id)
    elif request.difficulty:
        task = get_task_by_difficulty(request.difficulty)
    else:
        task = TASKS[0]

    CURRENT_STATE = _create_state(task)
    obs = _build_observation(CURRENT_STATE)

    return StepResponse(
        observation=obs,
        reward=0.0,
        done=False,
        info={
            "message": "Environment reset successful",
            "task_name": task.name,
        },
    )


@app.post("/step", response_model=StepResponse)
def step_env(action: StepRequest):
    state = _ensure_initialized()

    if state.done:
        return StepResponse(
            observation=_build_observation(state),
            reward=0.0,
            done=True,
            info={"final_grade": final_grade(state)},
        )

    state.step_count += 1
    state.history.append(
        Message(role="agent", content=f"[{action.action_type}] {action.content}")
    )

    reward, warnings, components = step_reward(state, action)

    state.warnings.extend(warnings)
    state.cumulative_reward += reward

    if action.action_type == ActionType.ASK_CUSTOMER:
        reply = _customer_reply_for_action(state, action)
        state.history.append(Message(role="customer", content=reply))

    if action.action_type == ActionType.ESCALATE:
        state.escalated = True

    if action.action_type == ActionType.PROPOSE_RESOLUTION:
        state.resolution_proposed = True

    if action.action_type == ActionType.CLOSE_CASE:
        state.case_closed = True
        state.done = True

    if state.step_count >= state.task.max_steps:
        state.done = True

    grade = final_grade(state)
    obs = _build_observation(state)

    # 🔥 NEW WINNING FEATURES
    decision_explanation = (
        f"Action '{action.action_type}' resulted in progress={components['progress']:.2f}, "
        f"risk_penalty={components['risk_penalty']:.2f}. "
        f"The system evaluates safety, correctness, and efficiency."
    )

    risk_score = max(0, 1 - len(state.risk_mistakes) * 0.25)

    trajectory_summary = None
    if state.done:
        trajectory_summary = {
            "total_steps": state.step_count,
            "mistakes": state.risk_mistakes,
            "efficiency": grade["efficiency"],
        }

    return StepResponse(
        observation=obs,
        reward=reward,
        done=state.done,
        info={
            "cumulative_reward": round(state.cumulative_reward, 4),
            "step_components": components,
            "final_grade": grade if state.done else None,

            # 🔥 UPGRADE FEATURES
            "decision_explanation": decision_explanation,
            "risk_score": round(risk_score, 2),
            "trajectory_summary": trajectory_summary,
        },
    )


@app.get("/state")
def get_state():
    state = _ensure_initialized()
    grade = final_grade(state)

    return {
        "episode_id": state.episode_id,
        "task_id": state.task.task_id,
        "step_count": state.step_count,
        "done": state.done,
        "cumulative_reward": state.cumulative_reward,
        "risk_mistakes": state.risk_mistakes,
        "grade": grade,
    }


@app.get("/tasks")
def list_tasks():
    return {"tasks": [t.task_id for t in TASKS]}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )