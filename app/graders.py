from typing import Dict


def step_reward(state: Dict) -> float:
    """
    Simple step reward function
    """
    return 0.1


def final_grade(state: Dict) -> float:
    """
    Final grading function required by validator
    """
    return 1.0