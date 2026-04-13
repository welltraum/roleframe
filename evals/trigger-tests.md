<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->
# Trigger Tests

Verify that `/roleframe` activates on relevant queries and does NOT activate on unrelated ones.

## Should trigger

| # | Query | Expected mode |
|---|---|---|
| 1 | `/roleframe design agent Agent for processing product return requests` | design |
| 2 | `/roleframe review agent agents/1c` | review |
| 3 | `Спроектируй агента для обработки заявок` | design |
| 4 | `Проведи аудит агентов` | review |
| 5 | `/roleframe review` | review |
| 6 | `/roleframe` | help |
| 7 | `I need to design a workflow for customer support` | design |
| 8 | `Audit the pack maturity` | review |
| 9 | `/roleframe design pack Pack for donor skill intake` | design |
| 10 | `/roleframe review pack evals/files/sample-pack` | review |

## Should NOT trigger

| # | Query | Why not |
|---|---|---|
| 1 | `Write a Python script for data processing` | The skill must not activate. The task should be handled as a normal coding request. |
| 2 | `Fix the bug in supervisor.py` | The skill must not activate. |
| 3 | `Create a dashboard for sales metrics` | The skill must not activate because the request is not about governance-unit design or review. |
| 4 | `What is IDEF0?` | The skill must not auto-activate because this is an informational question. |
| 5 | `Help me with my 1C configuration` | The skill must not activate because the request is domain support, not governance-unit design. |

## How to test

1. Start a fresh Codex session in this project.
2. Run each query from `Should trigger` and verify the mode selection.
3. Run each query from `Should NOT trigger` and verify the skill does not hijack the task.
4. Save the raw response into the matching `outputs/response.md` file before grading.

## Results log

| # | Query | Expected | Actual | Pass? |
|---|---|---|---|---|
| | | | | |
