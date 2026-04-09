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


# ✅ ADD THIS (VERY IMPORTANT)
def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()