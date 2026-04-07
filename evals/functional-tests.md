<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->
# Functional Tests

Verify that each mode produces correct, complete output.

Review outputs must follow the canonical audit package defined in `references/audit-template.md`,
including evidence-based scoring, backlog actions, and generated dashboard artifacts when applicable.

## Mode: design

### Test D1: A full single-agent design package with IDEF0 and explicit control/mechanism split.

**Input:** `/roleframe design Agent that converts a fuzzy user request into a structured query to a product catalog`

**Expected behavior:**
- [ ] The response asks clarifying questions about business function, consumer, inputs, and output format.
- [ ] The response contains an IDEF0 card with Input, Control, Mechanism, and Output.
- [ ] The response labels what belongs to Control and what belongs to Mechanism.
- [ ] The output contract covers happy path, business-empty, and tool failure.
- [ ] The response uses the passport template concept.

### Test D2: A decomposed multi-agent design with supervisor and routing contract.

**Input:** `/roleframe design System for end-to-end processing of tax authority requests: extract requirements, find documents, prepare response, archive`

**Expected behavior:**
- [ ] The response rejects a single-agent framing as too broad.
- [ ] The response proposes 3 to 4 agents with rationale.
- [ ] The response includes a supervisor or routing role.
- [ ] The response defines a routing contract between agents.
- [ ] The response includes a relationship diagram in Mermaid or equivalent structured form.

### Test D3: The skill pushes back on the vague brief and asks for a concrete business result.

**Input:** `/roleframe design Smart assistant for our company`

**Expected behavior:**
- [ ] The response does not accept the vague request as-is.
- [ ] The response asks what specific business result the agent must return.
- [ ] The response hints at decomposition if the user describes multiple functions.

## Mode: review

### Test R1: A full review over the fixture agents with evidence-driven findings, audit markdown files, and a dashboard build.

**Input:** `/roleframe review evals/files/sample-agents/agents`

**Expected behavior:**
- [ ] The response discovers all fixture agent files.
- [ ] The response resolves the placeholder include used by the supervisor fixture.
- [ ] The response cites concrete file paths or file:line evidence.
- [ ] The response scores maturity criteria or uses an explicit audit rubric.
- [ ] The response includes cross-agent analysis or overlap findings.
- [ ] The response creates or clearly intends an audit package and dashboard HTML as review artifacts.

### Test R2: The skill uses default discovery when no path argument is supplied.

**Input:** `/roleframe review`

**Expected behavior:**
- [ ] The response mentions default search under agents/.
- [ ] The response stays in review mode.
- [ ] The response does not require a path before it can explain the workflow.

### Test R3: The skill reviews a single agent artifact deeply, still using the audit structure and still producing review artifacts.

**Input:** `/roleframe review evals/files/sample-agents/agents/supervisor.md`

**Expected behavior:**
- [ ] The response scopes the review to the supplied file.
- [ ] The response still applies the audit structure.
- [ ] The response still includes evidence and checklist-style findings.
- [ ] The response still treats review as an artifact-producing workflow rather than a one-off text critique.

## Mode: dashboard

### Test B1: A dashboard build using the fixture audits and the bundled HTML template.

**Input:** `/roleframe dashboard evals/files/sample-audits`

**Expected behavior:**
- [ ] The response reads audit markdown files as input.
- [ ] The response references the bundled HTML template.
- [ ] The output target is docs/agent_audit/dashboard.html.
- [ ] The response expects overview, methodology, agents, and issues views.
- [ ] The response does not generate an unrelated dashboard structure.

### Test B2: The skill detects that no audit files exist and suggests review first.

**Input:** `/roleframe dashboard docs/empty_audits`

**Expected behavior:**
- [ ] The response states that no audit files were found.
- [ ] The response suggests running /roleframe review first.
- [ ] The response does not claim success with an empty dashboard.

## Eval workflow checks

- Before grading `review`, verify the raw response, audit markdown files, summary, and `dashboard.html`.
- Before grading `dashboard`, verify the raw response and any expected dashboard artifact rules from `evals/evals.json`.
- Run the first wave before the second wave in the risk-based cycle.
