from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

# Simple in-memory state
ENV_STATE: Dict[str, Any] = {}


class StepInput(BaseModel):
    action: str = ""
    content: str = ""


@app.get("/")
def root():
    return {"message": "SupportOpsEnv running"}


# ✅ REQUIRED: RESET ENDPOINT
@app.post("/reset")
def reset():
    global ENV_STATE
    ENV_STATE = {
        "messages": [],
        "done": False
    }

    return {
        "status": "reset successful",
        "state": ENV_STATE
    }


# ✅ REQUIRED: STEP ENDPOINT (important for next phase)
@app.post("/step")
def step(input: StepInput):
    ENV_STATE["messages"].append(input.content)

    return {
        "observation": "Step processed",
        "reward": 0.1,
        "done": False,
        "info": {}
    }


# ✅ OPTIONAL BUT SAFE
@app.get("/health")
def health():
    return {"status": "ok"}