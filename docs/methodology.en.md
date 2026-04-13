# Governance unit methodology

This document is based on `Инженерия агентов 2026`. It is the short reference for reading RoleFrame dashboards and structured packages after the move from agent-only framing to governance units.

## 1. A governance unit is not just a prompt

An LLM is not the system. A governance unit starts where policy, runtime, routes, tests, and operating signals are attached to the model:

- constraints and SOP
- tools and adapters
- manifests and ownership markers
- output contracts
- eval and observability
- rollout and preparedness signals

Without those layers, you only have a prompt prototype.

## 2. Three profiles

RoleFrame keeps one core method, but it now supports three profiles:

- `agent`, one business function
- `pack`, one ownership boundary with explicit routes and proof surfaces
- `workflow`, one orchestration contour that must be decomposed before audit

Profile rules:

- `agent`: reject "does everything" briefs
- `pack`: reject parallel owner surfaces
- `workflow`: map the contour, then split it into units

## 3. IDEF0 stays unchanged

IDEF0 is still the requirement frame.

### Input

What enters the unit:

- request
- event
- file
- handoff
- route payload

### Control

What governs the unit:

- role
- SOP
- constraints
- contract
- decision rules

Prompt and policy files live here.

### Mechanism

What executes the unit:

- tools
- runtime
- manifests
- routes
- memory
- adapters
- rollout helpers

### Output

What counts as completion:

- success
- business-empty
- technical failure
- partial / refusal
- delegation
- rollout or visibility signal

## 4. The minimum design rule is profile-aware

Use the same question in different forms:

- `agent`: what is the one business function?
- `pack`: what is the one owner boundary?
- `workflow`: what must be decomposed before the boundary is honest?

If you cannot answer that in one sentence, the current unit is too broad.

## 5. Evidence precedence in review

Trust artifacts in this order:

1. runtime, manifests, adapters, tests, proof surfaces
2. prompts and policy files
3. prose docs

If the prompt says one thing but the route, test, or manifest proves another, trust the executable or proof layer.

## 6. What good control looks like

Control must fix:

- identity
- narrow responsibility
- ordered SOP
- constraints
- typed output contract

For pack review, control also states route discipline and ownership rules. For workflow review, control must state decomposition and escalation rules.

## 7. What good mechanism looks like

Mechanism must make the contract real:

- tools and rights are explicit
- routes are typed
- retry and timeout policy are bounded
- owned surfaces and visible surfaces do not conflict
- tests and proof surfaces exist for the risky claims

## 8. What eval must cover

Eval must include:

- happy path
- edge cases
- business-empty
- failure paths
- partial or refusal paths
- routing mistakes
- ownership conflicts
- proof-surface drift

## 9. Practical minimum

Before implementation or rollout, a governance unit should have at least:

1. a fixed profile
2. a clear boundary statement
3. an IDEF0 card
4. typed contracts
5. governance data: owner boundary, routes, owned surfaces, proof surfaces
6. evaluation scenarios
7. rollout and observability signals

If these artifacts do not exist, the team is still tuning behavior by feel.
