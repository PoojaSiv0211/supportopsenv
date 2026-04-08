import os
import requests

# ==============================
# ENV VARIABLES (REQUIRED FORMAT)
# ==============================
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://poojasiv0211-supportopsenv.hf.space"
)

MODEL_NAME = os.getenv("MODEL_NAME", "support-agent")
HF_TOKEN = os.getenv("HF_TOKEN")  # optional


# ==============================
# API FUNCTIONS
# ==============================
def reset():
    res = requests.post(
        f"{API_BASE_URL}/reset",
        json={"difficulty": "hard"}
    )
    res.raise_for_status()
    return res.json()


def step(action_type, content):
    res = requests.post(
        f"{API_BASE_URL}/step",
        json={
            "action_type": action_type,
            "content": content
        }
    )
    res.raise_for_status()
    return res.json()


# ==============================
# MAIN EXECUTION
# ==============================
def run_episode():
    print("START")

    state = reset()
    print("RESET:", state["observation"]["task_id"])

    steps = [
        ("analyze", "This is a security breach. Preserve logs and treat as incident."),
        ("internal_note", "Preserve logs and audit trails. Do not delete evidence."),
        ("ask_customer", "What data was exported and can you rotate credentials now?"),
        ("escalate", "Escalating to security incident response team."),
        ("propose_resolution", "Containment: revoke sessions, rotate credentials, preserve logs."),
    ]

    final_response = None

    for action, text in steps:
        res = step(action, text)
        final_response = res

        print(f"STEP: {action} | reward: {res['reward']}")

        # 🔥 WINNING ADDITIONS
        if res["info"].get("decision_explanation"):
            print("EXPLAIN:", res["info"]["decision_explanation"])

        if res["info"].get("risk_score") is not None:
            print("RISK:", res["info"]["risk_score"])

        if res["done"]:
            break

    # FINAL OUTPUT
    if final_response:
        print("FINAL SCORE:", final_response["info"].get("final_grade"))

        if final_response["info"].get("trajectory_summary"):
            print("TRAJECTORY:", final_response["info"]["trajectory_summary"])

    print("END")


if __name__ == "__main__":
    run_episode()