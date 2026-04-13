<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->
# Performance Comparison: With vs Without Skill

Use these cases for a structured with-skill vs without-skill comparison.

## Cases

### comparison-a

**Prompt:** `Design an agent for processing product return requests`

**Expected improvement:** With the skill, the design should be more structured than the baseline and include IDEF0, governance, explicit contracts, and delivery planning.

**Assertions:**
- [ ] The with-skill output contains an IDEF0 structure.
- [ ] The with-skill output contains a three-path output contract.
- [ ] The with-skill output distinguishes Control from Mechanism.

### comparison-b

**Prompt:** `Review the agent in evals/files/sample-agents/agents/supervisor.md`

**Expected improvement:** With the skill, the review should be more discovery-driven, evidence-driven, and structured than the baseline.

**Assertions:**
- [ ] The with-skill output contains a stable audit structure.
- [ ] The with-skill output cites file evidence.
- [ ] The with-skill output includes actionable backlog items.

### comparison-c

**Prompt:** `Review the pack in evals/files/sample-pack`

**Expected improvement:** With the skill, the review should inventory manifests, routes, proofs, and rollout signals instead of relying on prompt-only critique.

**Assertions:**
- [ ] The with-skill output inventories pack artifacts.
- [ ] The with-skill output cites manifest or proof evidence.
- [ ] The with-skill output includes governance findings.

## Results log

| Test | Without skill (notes) | With skill (notes) | Improvement? |
|---|---|---|---|
| | | | |
