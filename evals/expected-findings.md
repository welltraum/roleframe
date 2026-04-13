# Expected findings for the sample review testbed

Use this file as the acceptance baseline for `review` on [`evals/files/sample-agents/`](./files/sample-agents/).

The goal is not to force identical wording. The goal is to make sure the skill consistently finds the same engineering defects with evidence and actionable backlog.

## Canonical finding categories

| Category | Expected signal | Primary evidence target |
|---|---|---|
| Supervisor scope is too broad | The review says the supervisor mixes routing and final response assembly in one role. | `evals/files/sample-agents/agents/supervisor.md`, `evals/files/sample-agents/prompts/agents/supervisor.txt` |
| Routing contract is implicit | The review says delegation rules exist only in prose and handoff payloads are not typed. | `evals/files/sample-agents/prompts/agents/supervisor.txt` |
| Output contract is missing | The review flags free-form output for supervisor and missing strict schema for downstream consumers. | `evals/files/sample-agents/prompts/agents/supervisor.txt` |
| Hidden or weak tool assumptions | The review catches `archive_search` as an undeclared dependency or weak tool policy. | `evals/files/sample-agents/prompts/agents/supervisor.txt`, `evals/files/sample-agents/src/tools/factory.py` |
| Tool failure strategy is weak | The review flags that document-finder has no reliable timeout or failure policy. | `evals/files/sample-agents/agents/document-finder.md` |
| Handoff payload is untyped | The review says document-finder passes results without a fixed structure. | `evals/files/sample-agents/agents/document-finder.md` |
| Unsafe completion behavior exists | The review flags that response-drafter is allowed to fill gaps from context. | `evals/files/sample-agents/agents/response-drafter.md` |
| Eval and ops gaps remain | The review says the fixture exists, but unit-level eval coverage, observability, and change checks are still partial. | `evals/evals.json`, `evals/functional-tests.md`, absence in sample agent-profile fixture |

## Acceptance rule

`review` passes this baseline when all of the following are true:

- At least 5 of the 8 canonical finding categories appear in the audit package.
- The generated findings cite file evidence with `file:line` or `file#Lx-Ly`.
- The backlog contains concrete actions, not only summaries.
- Cross-unit analysis mentions the supervisor handoff problem when more than one fixture unit is reviewed.

## Notes for evaluators

- Do not require the exact anti-pattern code if the same engineering defect is identified clearly.
- Prefer evidence quality over wording similarity.
- If the skill misses a category but finds a stronger adjacent defect from the same source file, count that as a partial pass and note it in grading.
