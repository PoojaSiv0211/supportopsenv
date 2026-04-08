from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from app.graders import compute_progress_score, final_task_grade
from app.models import (
    Action,
    CustomerProfile,
    KBArticle,
    Observation,
    PolicyRule,
    Reward,
    State,
    StepResponse,
    Ticket,
)
from app.tasks import TASKS, get_task_by_id


class SupportOpsEnv:
    def __init__(self) -> None:
        self._state: Optional[State] = None
        self._task_index = 0

    def reset(self, task_id: Optional[str] = None) -> Observation:
        if task_id is None:
            task = TASKS[self._task_index % len(TASKS)]
            self._task_index += 1
        else:
            task = get_task_by_id(task_id)

        extra_hidden = task.get("extra_hidden_fields", {})

        visible_fields = deepcopy(task["ticket"]["visible_fields"])
        visible_fields.setdefault("known_customer_plan", task["customer_profile"]["plan"])

        # Hard task keeps one hidden detail outside visible state
        for hidden_key in extra_hidden.keys():
            visible_fields.pop(hidden_key, None)

        self._state = State(
            task_id=task["task_id"],
            difficulty=task["difficulty"],
            done=False,
            ticket=Ticket(
                ticket_id=task["ticket"]["ticket_id"],
                customer_message=task["ticket"]["customer_message"],
                customer_id=task["ticket"]["customer_id"],
                visible_fields=visible_fields,
            ),
            customer_profile=CustomerProfile(**task["customer_profile"]),
            kb_articles=[KBArticle(**a) for a in task["kb_articles"]],
            policy_rules=[PolicyRule(**r) for r in task["policy_rules"]],
            hidden_gold=deepcopy(task["hidden_gold"] | extra_hidden),
            current_labels={
                "category": None,
                "priority": None,
                "resolution_code": None,
                "escalated": False,
                "closed": False,
            },
            requested_fields=[],
            retrieved_context=[],
            action_history=[],
            cumulative_reward=0.0,
            step_count=0,
            max_steps=task["max_steps"],
            unsafe_action_count=0,
            invalid_action_count=0,
            loop_count=0,
        )
        return self._build_observation("Environment reset successfully.")

    def state(self) -> Dict[str, Any]:
        self._ensure_initialized()
        assert self._state is not None
        return self._state.model_dump()

    def step(self, action: Action) -> StepResponse:
        self._ensure_initialized()
        assert self._state is not None

        if self._state.done:
            obs = self._build_observation("Episode already finished.")
            return StepResponse(
                observation=obs,
                reward=Reward(score=0.0, reason="No reward after termination."),
                done=True,
                info={"warning": "episode_already_done"},
            )

        self._state.step_count += 1

        reward_delta = 0.0
        notes = "Action processed."
        info: Dict[str, Any] = {}

        valid = self._apply_action(action)
        self._state.action_history.append(
            {
                "step": self._state.step_count,
                "action_type": action.action_type,
                "arguments": action.arguments,
                "valid": valid,
            }
        )

        if not valid:
            self._state.invalid_action_count += 1
            reward_delta -= 0.05
            notes = "Invalid or incomplete action."

        progress_score, rubric = compute_progress_score(self._state.model_dump())
        info["rubric"] = rubric

        # Convert progress movement into shaped reward
        prior_reward = self._state.cumulative_reward
        reward_delta += max(0.0, progress_score - prior_reward)

        # small step tax to discourage unnecessary wandering
        reward_delta -= 0.01

        done = False

        if self._state.step_count >= self._state.max_steps:
            done = True
            notes = "Reached maximum steps."

        if action.action_type in ("close_ticket", "escalate_ticket"):
            done = True
            notes = f"Terminal action reached: {action.action_type}."

        if self._state.invalid_action_count >= 4:
            done = True
            notes = "Too many invalid actions."

        if self._state.unsafe_action_count >= 2:
            done = True
            notes = "Too many unsafe actions."

        if done:
            final_score, final_rubric = final_task_grade(self._state.model_dump())
            reward_delta = max(0.0, final_score - self._state.cumulative_reward)
            info["final_rubric"] = final_rubric
            self._state.cumulative_reward = final_score
            self._state.done = True
        else:
            self._state.cumulative_reward = max(
                self._state.cumulative_reward,
                round(min(1.0, prior_reward + max(-0.05, reward_delta)), 4),
            )

        obs = self._build_observation(notes)
        reward = Reward(
            score=round(max(0.0, min(1.0, self._state.cumulative_reward)), 4),
            reason=notes,
        )

        return StepResponse(
            observation=obs,
            reward=reward,
            done=self._state.done,
            info=info,
        )

    def _apply_action(self, action: Action) -> bool:
        assert self._state is not None
        gold = self._state.hidden_gold

        if action.action_type == "inspect_ticket":
            self._state.retrieved_context.append(
                f"TICKET::{self._state.ticket.ticket_id}::{self._state.ticket.customer_message}"
            )
            return True

        if action.action_type == "inspect_customer":
            cp = self._state.customer_profile
            self._state.retrieved_context.append(
                f"CUSTOMER::{cp.customer_id}::plan={cp.plan};past_tickets={cp.past_tickets};"
                f"abuse_flags={cp.abuse_flags};failed_payments={cp.failed_payments}"
            )
            return True

        if action.action_type == "inspect_policy":
            for rule in self._state.policy_rules:
                self._state.retrieved_context.append(
                    f"POLICY::{rule.rule_id}::{rule.title}"
                )
            return True

        if action.action_type == "search_kb":
            query = str(action.arguments.get("query", "")).lower().strip()
            if not query:
                return False
            matched = 0
            for article in self._state.kb_articles:
                haystack = " ".join([article.title, article.content, " ".join(article.tags)]).lower()
                if any(word in haystack for word in query.split()):
                    self._state.retrieved_context.append(
                        f"KB::{article.article_id}::{article.title}"
                    )
                    matched += 1
            return matched > 0

        if action.action_type == "request_missing_info":
            fields = action.arguments.get("fields", [])
            if not isinstance(fields, list) or not fields:
                return False
            for field in fields:
                if field not in self._state.requested_fields:
                    self._state.requested_fields.append(field)
            return True

        if action.action_type == "assign_category":
            category = action.arguments.get("category")
            if not isinstance(category, str) or not category.strip():
                return False
            self._state.current_labels["category"] = category.strip()
            return True

        if action.action_type == "assign_priority":
            priority = action.arguments.get("priority")
            if priority not in {"low", "medium", "high", "urgent"}:
                return False
            self._state.current_labels["priority"] = priority
            return True

        if action.action_type == "propose_resolution":
            resolution_code = action.arguments.get("resolution_code")
            if not isinstance(resolution_code, str) or not resolution_code.strip():
                return False
            self._state.current_labels["resolution_code"] = resolution_code.strip()
            return True

        if action.action_type == "escalate_ticket":
            team = action.arguments.get("team")
            if not isinstance(team, str) or not team.strip():
                return False
            self._state.current_labels["escalated"] = True

            # Unsafe if escalating the easy case
            if not gold["should_escalate"]:
                self._state.unsafe_action_count += 1
            return True

        if action.action_type == "close_ticket":
            self._state.current_labels["closed"] = True

            # Unsafe if case should have escalated instead
            if gold["should_escalate"]:
                self._state.unsafe_action_count += 1
            return True

        return False

    def _build_observation(self, notes: str) -> Observation:
        assert self._state is not None
        gold = self._state.hidden_gold

        missing_fields = []
        for field in gold.get("required_missing_fields", []):
            if field not in self._state.requested_fields:
                missing_fields.append(field)

        return Observation(
            task_id=self._state.task_id,
            difficulty=self._state.difficulty,
            ticket_id=self._state.ticket.ticket_id,
            customer_message=self._state.ticket.customer_message,
            visible_fields=deepcopy(self._state.ticket.visible_fields),
            retrieved_context=deepcopy(self._state.retrieved_context[-8:]),
            missing_fields=missing_fields,
            action_history=deepcopy(self._state.action_history),
            step_count=self._state.step_count,
            steps_remaining=max(0, self._state.max_steps - self._state.step_count),
            available_actions=[
                "inspect_ticket",
                "inspect_customer",
                "inspect_policy",
                "search_kb",
                "request_missing_info",
                "assign_category",
                "assign_priority",
                "propose_resolution",
                "escalate_ticket",
                "close_ticket",
            ],
            notes=notes,
        )

    def _ensure_initialized(self) -> None:
        if self._state is None:
            raise RuntimeError("Environment is not initialized. Call reset() first.")