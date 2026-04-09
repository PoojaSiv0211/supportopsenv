from typing import Dict


def step_reward(state: Dict) -> Dict:
    return {"reward": 0.1}


def final_grade(state: Dict) -> Dict:
    return {"reward": 1.0}