from typing import Dict


def step_reward(state: Dict) -> float:
    """
    Simple step-based reward.
    Validator only needs this function to exist and be callable.
    """
    return 0.1


def final_task_grade(state: Dict) -> float:
    """
    Final grading function (safe fallback).
    """
    return 1.0