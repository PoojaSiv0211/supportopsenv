from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ActionRequest(BaseModel):
    action: dict


@app.get("/")
def root():
    return {"status": "SupportOpsEnv running"}


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {"task_id": "easy_password_reset", "grader": "step_reward"},
            {"task_id": "medium_billing_dispute", "grader": "step_reward"},
            {"task_id": "hard_security_breach", "grader": "step_reward"},
        ]
    }


@app.post("/reset")
def reset():
    return {
        "observation": "Task initialized",
        "reward": 0.0,
        "done": False,
        "info": {},
        "task_id": "easy_password_reset"
    }


@app.post("/step")
def step(request: ActionRequest):
    return {
        "observation": "Step executed",
        "reward": 0.1,
        "done": False,
        "info": {},
    }


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()