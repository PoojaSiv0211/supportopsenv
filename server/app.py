from fastapi import FastAPI
from app.env import SupportOpsEnv

app = FastAPI()

# Create environment instance
env = SupportOpsEnv()


@app.get("/")
def root():
    return {"message": "OpenEnv running"}


# ✅ FIXED RESET (THIS IS WHAT VALIDATOR NEEDS)
@app.post("/reset")
def reset():
    try:
        obs = env.reset()

        return {
            "observation": obs,
            "done": False,
            "info": {}
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# ✅ STEP ENDPOINT
@app.post("/step")
def step(action: dict):
    try:
        obs, reward, done, info = env.step(action)

        return {
            "observation": obs,
            "reward": reward,
            "done": done,
            "info": info
        }

    except Exception as e:
        return {
            "error": str(e)
        }


# health check
@app.get("/health")
def health():
    return {"status": "ok"}