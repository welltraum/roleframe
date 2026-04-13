# RoleFrame checklist

Use this checklist in `design` and `review`. The questions are stable, but the interpretation of boundary depends on the profile.

## Checklist

| # | Check item | Layer |
|---|---|---|
| 1 | The profile is fixed and the boundary is honest. `agent` = one function, `pack` = one owner boundary, `workflow` = decomposition-first. | Boundary |
| 2 | The IDEF0 card is explicit and no quadrant is vague. | Full model |
| 3 | Role, SOP, constraints, and typed contract exist in `Control`. | Control |
| 4 | Output covers success, empty, failure, and delegation or partial paths where needed. | Output |
| 5 | Prompt and policy stay in `Control`, while runtime details stay out of the prompt. | Control |
| 6 | Tools, adapters, routes, and rights match the actual executable surface. | Mechanism |
| 7 | Retry, timeout, step limits, and give-up rules are explicit. | Mechanism |
| 8 | Context and payload bounds are explicit. | Mechanism |
| 9 | Governance exists: owner boundary, routes, owned surfaces, proof surfaces, deployment visibility, rollout, preparedness. | Governance |
| 10 | Tests, eval scenarios, or proof surfaces exist for risky claims. | Evaluation |
| 11 | Observability exists for route choice, failure, empty result, and rollout state. | Operations |
| 12 | Safety guardrails enforce honest failure and explicit-only behavior. | Safety |
| 13 | Change management ties prompt, route, and runtime edits to regression. | Evolution |
| 14 | Dashboard is treated as derived output, not as canonical truth. | Artifact discipline |

## Red flags

Auto-fail the corresponding item if you find:

- no typed contract at all
- route payloads defined only in prose
- proof claims with no proof surfaces
- parallel owner surfaces inside one pack
- visible surfaces that the unit does not own
- dashboard treated as the primary source of truth
