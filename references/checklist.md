# RoleFrame Checklist: Is the Agent Well-Designed?

Use this checklist to validate an agent design (mode: design) or during audit (mode: review). Every item maps to an IDEF0 component.

## How to use

- For **design**: fill during Step 4 (validation). All items should be PASS before generating artifacts.
- For **review**: evaluate each item for the existing agent. Score PASS / PARTIAL / FAIL. Include evidence (file:line).

## Checklist

| # | Check item | IDEF0 | Status | Evidence / Notes |
|---|---|---|---|---|
| 1 | **Business function is fixed** and does not conflict with neighboring agents. The function is described as a concrete action, not "helps with". | Boundary | | |
| 2 | **IDEF0 card is filled**: Input, Control, Mechanism, Output are explicitly documented. No quadrant is empty or vague. | Full model | | |
| 3 | **Role, SOP, constraints exist** in the system prompt. The agent knows WHO it is, WHAT steps to follow, and WHAT it must NOT do. | **Control** | | |
| 4 | **Output contract is strict**: the format of the output is defined (JSON schema, enum of variants, or structured template). The consumer can parse it programmatically. | **Control -> Output** | | |
| 5 | **Skill/system prompt explicitly serves as Control in IDEF0.** There is a clear separation between rules (prompt) and implementation (code/tools). The prompt does not contain tool implementation logic. | **Control** | | |
| 6 | **Output covers non-happy paths**: behavior is defined for (a) business-empty results (no data found) and (b) tool/MCP unavailability (graceful degradation, not crash or hallucination). | **Output** | | |
| 7 | **Tools are described**: each tool has a purpose, rights are limited (not "can call anything"), and errors are handled. Tool descriptions match actual capabilities. | Mechanism | | |
| 8 | **Tool/MCP failure strategy exists**: for each tool/MCP, it is defined what happens on timeout, error, or unavailability. There is a fallback or explicit honest failure. | Mechanism | | |
| 9 | **Context management is defined**: static context (always present) is separated from dynamic context (loaded per request). There are rules for selection, truncation, and summarization. | Mechanism | | |
| 10 | **Runtime loop is bounded**: step limits exist, orchestrator handles errors, there is no possibility of infinite loops. Retry strategy is explicit. | Mechanism | | |
| 11 | **Evaluation exists**: there is a dataset with positive, negative, and edge-case scenarios. Metrics are defined. Regression runs are possible. | Quality | | |
| 12 | **Observability exists**: request logs, tool call outputs, cost/latency metrics, and rejection reasons are captured. It is possible to reconstruct what happened on any request. | Operations | | |
| 13 | **Safety guardrails exist**: permission limits, content restrictions, honest failure modes. The agent does not pretend to succeed when it failed. | Control + Mechanism | | |
| 14 | **Change management exists**: prompts are versioned, any edit goes through re-evaluation and regression comparison. There is a before/after quality check. | Evolution | | |

## Scoring guide for review mode

| Status | Meaning | Score contribution |
|---|---|---|
| PASS | Fully implemented and verifiable | Contributes to maturity score |
| PARTIAL | Present but incomplete or implicit | Partial contribution, note what is missing |
| FAIL | Absent or critically insufficient | Key deficit, add to backlog |

## Red flags (auto-FAIL)

These patterns automatically fail the corresponding checklist item:

- **No output contract at all** -> FAIL #4, #6
- **System prompt contains tool implementation code** (SQL queries, API calls hardcoded in prompt) -> FAIL #5
- **"Can use any tool"** without restrictions -> FAIL #7
- **No mention of what happens when tool fails** -> FAIL #8
- **No dataset or test scenarios exist anywhere** -> FAIL #11
- **Prompts are not in version control** -> FAIL #14
