import os
import requests

# REQUIRED ENV VARIABLES
API_BASE_URL = os.getenv("API_BASE_URL", "https://poojasiv0211-supportopsenv.hf.space")
MODEL_NAME = os.getenv("MODEL_NAME", "support-agent")
HF_TOKEN = os.getenv("HF_TOKEN")  # optional

def reset():
    res = requests.post(f"{API_BASE_URL}/reset", json={"difficulty": "hard"})
    return res.json()

def step(action_type, content):
    res = requests.post(
        f"{API_BASE_URL}/step",
        json={
            "action_type": action_type,
            "content": content
        }
    )
    return res.json()

def run_episode():
    print("START")

    state = reset()
    print("RESET:", state["observation"]["task_id"])

    steps = [
        ("analyze", "This is a security incident. Preserve logs."),
        ("ask_customer", "What data was exported?"),
        ("escalate", "Escalating to security team."),
        ("propose_resolution", "Revoke sessions and rotate credentials."),
    ]

    for action, text in steps:
        res = step(action, text)
        print("STEP:", action, "| reward:", res["reward"])

        if res["done"]:
            break
    print("FINAL SCORE:", res["info"].get("final_grade"))
    print("END")

if __name__ == "__main__":
    run_episode()