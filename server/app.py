from fastapi import FastAPI

app = FastAPI()


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
    return {"observation": "ok", "done": False, "info": {}}


@app.post("/step")
def step(action: dict):
    return {
        "observation": "ok",
        "reward": 0.1,
        "done": False,
        "info": {},
    }


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()