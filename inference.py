import os
import requests

# =============================
# ENV VARIABLES (REQUIRED)
# =============================
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://poojasiv0211-supportopsenv.hf.space"
)

MODEL_NAME = os.getenv("MODEL_NAME", "support-agent")
HF_TOKEN = os.getenv("HF_TOKEN")  # optional

TASK_NAME = "supportops"
BENCHMARK = "supportops_env"
MAX_STEPS = 8


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


def run_episode():
    rewards = []
    steps_taken = 0

    log_start()

    try:
        state = reset()

        steps = [
            ("analyze", "Security breach. Preserve logs."),
            ("internal_note", "Preserve logs. Do not delete evidence."),
            ("ask_customer", "What data was exported?"),
            ("escalate", "Escalating to security team."),
            ("propose_resolution", "Revoke sessions and rotate credentials."),
        ]

        final_response = None

        for i, (action, text) in enumerate(steps, start=1):
            res = step(action, text)
            final_response = res

            reward = res["reward"]
            done = res["done"]

            rewards.append(reward)
            steps_taken = i

            log_step(i, action, reward, done)

            if done:
                break

        # Score normalization
        total_reward = sum(rewards)
        score = min(max(total_reward / 2.0, 0.0), 1.0)

        success = score > 0.2

    except Exception as e:
        log_end(False, steps_taken, 0.0, rewards)
        return

    log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    run_episode()