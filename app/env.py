from typing import Dict, Any

from app.tasks import get_task_by_difficulty
from app.models import Difficulty, EnvironmentState, StepRequest, ActionType
from app.graders import step_reward, final_grade


# 🔥 GRADER MAPPING (IMPORTANT)
GRADER_MAP = {
    "step_reward": step_reward
}


class SupportOpsEnv:
    def __init__(self):
        self.state: EnvironmentState | None = None

    def reset(self) -> str:
        task = get_task_by_difficulty(Difficulty.EASY)

        self.state = EnvironmentState(
            task=task,
            step_count=0,
            gathered_facts={},
            asked_for_customer_info=[],
            risk_mistakes=[],
            escalated=False,
            resolution_proposed=False,
            case_closed=False,
            duplicate_question_count=0,
        )

        return f"Task: {task.name} | {task.initial_ticket.description}"

    def step(self, action_dict: Dict[str, Any]):
        if self.state is None:
            raise ValueError("Call reset() first")

        action_type = action_dict.get("action", "ANALYZE")
        content = action_dict.get("content", "")

        action = StepRequest(
            action_type=ActionType[action_type],
            content=content
        )

        # ✅ USE STRING → FUNCTION MAPPING
        grader_fn = GRADER_MAP[self.state.task.grader]

        reward, warnings, components = grader_fn(self.state, action)

        self.state.step_count += 1

        done = self.state.step_count >= self.state.task.max_steps

        info = {
            "warnings": warnings,
            "components": components
        }

        if done:
            info["final_score"] = final_grade(self.state)

        return (
            f"Processed: {content}",
            reward,
            done,
            info
        )