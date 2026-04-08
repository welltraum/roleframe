<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->
# Functional Tests

Verify that each mode produces correct, complete output.

Design outputs must follow the structured design package and generate markdown plus dashboard artifacts.
Review outputs must follow the canonical audit package defined in `references/audit-template.md`.

## Mode: design

### Test D1: A full single-agent design package with IDEF0, explicit control/mechanism split, delivery plan, structured design JSON, and dashboard build.

**Input:** `/roleframe design Agent that converts a fuzzy user request into a structured query to a product catalog`

**Expected behavior:**
- [ ] The response asks about business function, consumer, inputs, success criteria, and output format.
- [ ] The response contains an IDEF0 card with Input, Control, Mechanism, and Output.
- [ ] The response labels what belongs to Control and what belongs to Mechanism.
- [ ] The response includes runtime, eval, observability, and change-management planning.
- [ ] The response creates or clearly intends structured design JSON, rendered markdown views, and dashboard HTML under docs/agent_design.

### Test D2: A decomposed multi-agent design package with routing contract, delivery plan, structured design artifacts, and dashboard build.

**Input:** `/roleframe design System for end-to-end processing of tax authority requests: extract requirements, find documents, prepare response, archive`

**Expected behavior:**
- [ ] The response rejects a single-agent framing as too broad.
- [ ] The response proposes 3 to 4 agents with rationale.
- [ ] The response includes a supervisor or routing role.
- [ ] The response defines a routing contract between agents.
- [ ] The response includes a delivery plan and creates or clearly intends docs/agent_design artifacts plus dashboard HTML.

### Test D3: The skill pushes back on the vague brief and asks for a concrete business result.

**Input:** `/roleframe design Smart assistant for our company`

**Expected behavior:**
- [ ] The response does not accept the vague request as-is.
- [ ] The response asks what specific business result the agent must return.
- [ ] The response hints at decomposition if the user describes multiple functions.

## Mode: review

### Test R1: A full review over the fixture agents with discovery, evidence-driven findings, structured audit JSON files, rendered markdown views, and a dashboard build.

**Input:** `/roleframe review evals/files/sample-agents/agents`

**Expected behavior:**
- [ ] The response starts with discovery or inventory of agent-related artifacts in the supplied path.
- [ ] The response discovers all fixture agent files.
- [ ] The response resolves the placeholder include used by the supervisor fixture.
- [ ] The response cites concrete file paths or file:line evidence.
- [ ] The response includes cross-agent analysis or overlap findings.
- [ ] The response creates or clearly intends structured audit JSON, rendered markdown views, and dashboard HTML as review artifacts.

### Test R2: The skill uses project-root discovery when no path argument is supplied.

**Input:** `/roleframe review`

**Expected behavior:**
- [ ] The response mentions discovery from the project root or default project search.
- [ ] The response stays in review mode.
- [ ] The response does not require a path before it can explain the workflow.

### Test R3: The skill reviews a single agent artifact deeply, still using discovery for related assets and still producing review artifacts.

**Input:** `/roleframe review evals/files/sample-agents/agents/supervisor.md`

**Expected behavior:**
- [ ] The response scopes the review to the supplied file.
- [ ] The response still discovers related prompt, tool, or runtime assets.
- [ ] The response still applies the audit structure.
- [ ] The response still treats review as an artifact-producing workflow rather than a one-off text critique.

## Eval workflow checks

- Before grading `design`, verify the raw response, design markdown files, summary, and `dashboard.html`.
- Before grading `review`, verify the raw response, audit markdown files, summary, and `dashboard.html`.
- Run the first wave before the second wave in the risk-based cycle.
