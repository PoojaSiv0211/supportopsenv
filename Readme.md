---
title: SupportOpsEnv
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
---

# SupportOpsEnv

Risk-aware AI customer support environment for hackathon evaluation.

## Endpoints

- `GET /health`
- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /tasks`
- `GET /docs`

## Example

Reset to hard task:

```bash
curl -X POST https://YOUR-SPACE.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"difficulty":"hard"}'