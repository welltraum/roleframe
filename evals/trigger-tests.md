# Trigger Tests

Verify that `/roleframe` activates on relevant queries and does NOT activate on unrelated ones.

## Should trigger

| # | Query | Expected mode |
|---|---|---|
| 1 | `/roleframe design Agent for processing product return requests` | design |
| 2 | `/roleframe review agents/1c` | review |
| 3 | `/roleframe dashboard` | dashboard |
| 4 | `Спроектируй агента для обработки заявок` | design (auto-trigger) |
| 5 | `Проведи аудит агентов` | review (auto-trigger) |
| 6 | `Собери дашборд агентов` | dashboard (auto-trigger) |
| 7 | `/roleframe review` (no path) | review with auto-discovery |
| 8 | `/roleframe` (no args) | help message |
| 9 | `I need to design a multi-agent system for customer support` | design (auto-trigger) |
| 10 | `Audit the agent maturity` | review (auto-trigger) |

## Should NOT trigger

| # | Query | Why not |
|---|---|---|
| 1 | `Write a Python script for data processing` | Code task, not agent design |
| 2 | `Fix the bug in supervisor.py` | Bug fix, not methodology |
| 3 | `Create a dashboard for sales metrics` | Generic dashboard, not agent audit |
| 4 | `What is IDEF0?` | Informational question, not skill action |
| 5 | `Help me with my 1C configuration` | Domain task, not agent design |

## How to test

1. Start a fresh Claude Code session in this project
2. Run each query from "Should trigger" -- verify skill loads and correct mode is selected
3. Run each query from "Should NOT trigger" -- verify skill does NOT load
4. Record results in the table below

## Results log

| # | Query | Expected | Actual | Pass? |
|---|---|---|---|---|
| | | | | |
