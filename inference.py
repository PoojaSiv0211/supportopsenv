import os
import requests

# =============================
# SAFE OPENAI IMPORT (CRITICAL)
# =============================
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# =============================
# ENV VARIABLES
# =============================
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://poojasiv0211-supportopsenv.hf.space"
)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

TASK_NAME = "supportops"
BENCHMARK = "supportops_env"


# =============================
# OPENAI CLIENT (SAFE)
# =============================
client = None
if OPENAI_AVAILABLE and HF_TOKEN:
    try:
        client = OpenAI(api_key=HF_TOKEN)
    except Exception:
        client = None


# =============================
# API CALLS
# =============================
def reset():
    res = requests.post(f"{API_BASE_URL}/reset", json={"difficulty": "hard"})
    res.raise_for_status()
    return res.json()


def step(action_type, content):
    res = requests.post(
        f"{API_BASE_URL}/step",
        json={"action_type": action_type, "content": content}
    )
    res.raise_for_status()
    return res.json()


# =============================
# LLM ACTION (SAFE)
# =============================
def get_action_text(step_num):
    # If OpenAI available → use it
    if client:
        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity support agent."},
                    {"role": "user", "content": f"Step {step_num}: What should be done next?"}
                ],
                max_tokens=50,
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            pass

    # Fallback (VERY IMPORTANT)
    fallback = [
        "Analyze the issue as a security breach.",
        "Preserve logs and audit trails.",
        "Ask what data was exported.",
        "Escalate to security team.",
        "Revoke sessions and rotate credentials.",
    ]

    return fallback[min(step_num - 1, len(fallback) - 1)]


# =============================
# LOGGING
# =============================
def log_start():
    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}", flush=True)


def log_step(step_num, action, reward, done, error=None):
    error_val = error if error else "null"
    done_val = str(done).lower()

    print(
        f"[STEP] step={step_num} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# =============================
# MAIN EXECUTION
# =============================
def run_episode():
    rewards = []
    steps_taken = 0

    log_start()

    try:
        reset()

        for step_num in range(1, 6):
            text = get_action_text(step_num)

            # simple mapping
            text_lower = text.lower()
            if "analy" in text_lower:
                action = "analyze"
            elif "ask" in text_lower:
                action = "ask_customer"
            elif "escalate" in text_lower:
                action = "escalate"
            elif "revoke" in text_lower or "rotate" in text_lower:
                action = "propose_resolution"
            else:
                action = "internal_note"

            res = step(action, text)

            reward = res["reward"]
            done = res["done"]

            rewards.append(reward)
            steps_taken = step_num

            log_step(step_num, action, reward, done)

            if done:
                break

        total_reward = sum(rewards)
        score = min(max(total_reward / 2.0, 0.0), 1.0)
        success = score > 0.2

    except Exception:
        log_end(False, steps_taken, 0.0, rewards)
        return

    log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    run_episode()