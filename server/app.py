from fastapi import FastAPI, HTTPException

from app.env import SupportOpsEnv
from app.models import ResetRequest
from app.tasks import TASKS

app = FastAPI(title="SupportOpsEnv")

env = SupportOpsEnv()


@app.get("/")
def root():
    return {"message": "OpenEnv running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    from app.tasks import TASKS
    return {
        "tasks": [
            {
                "task_id": t.task_id,
                "grader": t.grader
            }
            for t in TASKS
        ]
    }


@app.post("/reset")
def reset(payload: ResetRequest | None = None):
    try:
        if payload is None:
            obs = env.reset()
        else:
            obs = env.reset(
                difficulty=payload.difficulty,
                task_id=payload.task_id,
            )

        return {
            "observation": obs,
            "done": False,
            "info": {},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step")
def step(action: dict):
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs,
            "reward": reward,
            "done": done,
            "info": info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))