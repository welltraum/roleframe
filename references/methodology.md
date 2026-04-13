# RoleFrame methodology reference

## Quick map

- Foundation
- Profiles
- IDEF0
- Maturity criteria
- Design workflow
- Review workflow
- Typical failure modes

## Foundation

RoleFrame treats the system as a **governance unit**, not as a loose chat prompt.

A governance unit is a designed boundary with:

- explicit `Control`
- executable `Mechanism`
- typed `Output`
- measurable quality and rollout discipline

## Profiles

| Profile | Design rule | Main review risk |
|---|---|---|
| `agent` | One business function | God prompt, implicit routing, free-form output |
| `pack` | One ownership boundary | Parallel owner surfaces, hidden routes, proof-surface drift |
| `workflow` | Decompose before audit | Treating a whole contour as one atomic function |

## IDEF0

```
         Control
    (role, SOP, constraints,
     contract = prompt / policy)
            |
            v
Input ---> [UNIT] ---> Output
            ^
            |
        Mechanism
    (tools, runtime, manifests, routes, memory)
```

### Key principle

Prompt and policy files are always `Control`.

Code, routes, manifests, tests, proof surfaces, and rollout helpers are never substitutes for `Control`, but they outrank prose claims during review.

## 10 maturity criteria

Each criterion stays `0..3` for compatibility.

| # | Criterion | Profile-aware interpretation |
|---|---|---|
| 1 | Business boundary | `agent`: atomic function, `pack`: owner boundary, `workflow`: honest decomposition boundary |
| 2 | Input definition | Requests, routes, files, and invalid states are explicit |
| 3 | Control layer | Role, SOP, constraints, and contract are explicit |
| 4 | Mechanism layer | Tools, adapters, manifests, and rights are explicit |
| 5 | Context engineering | Static and dynamic context, payload bounds, and route payload discipline are defined |
| 6 | Runtime loop | Step limits, retry, timeout, give-up, and orchestration boundaries are explicit |
| 7 | Evaluation | Scenarios, metrics, and proof surfaces exist |
| 8 | Observability | Logs, traces, rollout, and visibility signals exist |
| 9 | Safety | Honest failure, permission limits, and explicit-only discipline exist |
| 10 | Change management | Versioned changes, regression loop, and rollout gates exist |

### Score interpretation

| Range | Level | Description |
|---|---|---|
| `0-10` | Experiment | No stable engineering boundary |
| `11-20` | Working prototype | Main contract exists but major risks remain |
| `21-25` | Managed unit | Controlled and measurable |
| `26-30` | Mature component | Ready for safe reuse and rollout |

## Design workflow

1. Fix the profile.
2. Write one boundary sentence.
3. Fill IDEF0.
4. Separate `Control` from `Mechanism`.
5. Add typed contracts.
6. Add governance fields: owner boundary, routes, owned surfaces, proof surfaces, deployment visibility, rollout, preparedness.
7. Add evaluation and delivery plans.
8. Render JSON-first artifacts.

## Review workflow

1. Discover artifacts first.
2. Select or infer the profile.
3. Apply the right archaeology mode:
   - `agent`: prompt archaeology + runtime cross-check
   - `pack`: artifact archaeology
   - `workflow`: decomposition-first audit
4. Score the 10 criteria with evidence.
5. Build contract matrix and route matrix.
6. Extract patch plan and rollout risks.

## Evidence precedence

Trust order:

1. runtime, manifests, adapters, tests, proof surfaces
2. prompts and policy files
3. prose docs

This avoids false confidence from prompt-only archaeology.

## Typical failure modes

| Symptom | Probable root cause | First correction |
|---|---|---|
| One unit tries to do everything | Boundary is too broad | Decompose |
| Pack owns too many parallel surfaces | Ownership is not honest | Shrink to one owner boundary |
| Route exists only in prose | Contract is implicit | Type the route payload |
| Proof claims exist without proof surfaces | Governance is not verifiable | Add tests or artifact checks |
| Deployed unit is invisible or visible unit is not owned | Visibility and ownership drifted | Separate rollout from ownership and document both |
| Dashboard becomes canonical truth | Derived artifact is treated as source | Return to JSON-first package |
