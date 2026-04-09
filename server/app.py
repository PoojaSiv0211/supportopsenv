from fastapi import FastAPI

app = FastAPI()

# your routes here...


@app.get("/")
def root():
    return {"message": "OpenEnv running"}


@app.post("/reset")
def reset():
    # your logic
    return {"observation": "ok", "done": False, "info": {}}


@app.post("/step")
def step(action: dict):
    return {
        "observation": "ok",
        "reward": 0.1,
        "done": False,
        "info": {}
    }
@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "task_id": "easy_password_reset",
                "grader": "step_reward"
            },
            {
                "task_id": "medium_billing_dispute",
                "grader": "step_reward"
            },
            {
                "task_id": "hard_security_breach",
                "grader": "step_reward"
            }
        ]
    }

# ✅ ADD THIS (VERY IMPORTANT)
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()