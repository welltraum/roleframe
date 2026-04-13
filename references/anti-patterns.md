# Anti-pattern library

Use these during `review`. Name the pattern, cite evidence, explain the risk, and add a concrete backlog item.

## Control and contract anti-patterns

### AP-1: God Prompt
One prompt mixes routing, domain rules, file handling, and final formatting.

### AP-2: Implicit State Machine
The SOP exists only through examples and prose branches.

### AP-3: Prompt as Database
Static lookups, large enums, or data tables live inside the prompt.

### AP-4: Control-Mechanism Bleed
Prompt contains runtime constants, API wiring, or implementation details.

### AP-5: Role Identity Drift
The declared role and the actual instructions disagree.

### AP-6: Free-form Output
No machine-readable output contract exists.

### AP-7: Happy-path-only Contract
Success exists, but empty and failure paths do not.

### AP-8: Contract in Prose
The contract is described in words instead of a literal schema.

## Tool and runtime anti-patterns

### AP-9: Tool Hallucination Trap
Tools are declared but failure behavior is undefined.

### AP-10: Unbounded Tool Rights
The unit can call broad toolsets without usage rules.

### AP-11: Executor Scope Creep
Code execution or mutation rights exist without a narrow scope.

### AP-12: Missing Step Limit
No hard bound exists on retries, steps, or recursion.

## Structure and routing anti-patterns

### AP-13: Orphan Sub-unit
A sub-agent or dependent unit is declared but never given a valid invocation path.

### AP-14: Hidden Dependency
A prompt, route, or runtime path uses a tool or unit that is not declared.

### AP-15: Implicit Routing Contract
Routes exist, but the payload is untyped.

### AP-16: Untestable Unit
No eval scenarios, tests, or proof surfaces exist.

### AP-17: Trace Without Signal
Logs exist, but no product-level signal explains route choice, failure, or rollout state.

## Pack and governance anti-patterns

### AP-18: Explicit-only Violation
The pack claims explicit-only behavior, but runtime or routes allow undeclared behavior.

### AP-19: Parallel Owner Surfaces
One pack spreads ownership across multiple canonical surfaces with no single owner boundary.

### AP-20: Proof-surface Gap
Important claims in manifest, docs, or rollout notes are not backed by proof surfaces.

### AP-21: Deployed != Visible
The unit is deployed, but visibility rules or rollout state are undocumented or misleading.

### AP-22: Visible != Owned
The unit exposes a visible surface that it does not actually own.

### AP-23: Route Without Typed Contract
Adapter or route logic exists, but the handoff is only descriptive text.

### AP-24: Dashboard as Source of Truth
Teams treat dashboard HTML as canonical instead of the structured JSON package.
