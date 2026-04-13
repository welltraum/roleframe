<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->
# Functional Tests

Verify that each mode produces correct, complete output.

Design outputs must follow the structured design package and generate markdown plus dashboard artifacts.
Review outputs must follow the canonical audit package defined in `references/audit-template.md`.

## Mode: design

### Test D1: A full single-unit design package with IDEF0, explicit control/mechanism split, governance block, structured design JSON, and a dashboard build.

**Input:** `/roleframe design agent Agent that converts a fuzzy user request into a structured query to a product catalog`

**Expected behavior:**
- [ ] The response asks about boundary, consumer, inputs, success criteria, and output format.
- [ ] The response contains an IDEF0 card with Input, Control, Mechanism, and Output.
- [ ] The response labels what belongs to Control and what belongs to Mechanism.
- [ ] The response includes governance: owner boundary, routes, proof surfaces, rollout, and preparedness.
- [ ] The response creates or clearly intends structured design JSON, rendered markdown views, and dashboard HTML under docs/roleframe/design.

### Test D2: A decomposed workflow design package with route contracts, governance, structured design artifacts, and a dashboard build.

**Input:** `/roleframe design workflow System for end-to-end processing of tax authority requests: extract requirements, find documents, prepare response, archive`

**Expected behavior:**
- [ ] The response rejects a single-unit framing as too broad.
- [ ] The response proposes 3 to 4 child units with rationale.
- [ ] The response explicitly treats the brief as a workflow profile.
- [ ] The response defines route contracts between units.
- [ ] The response includes a delivery plan and creates or clearly intends docs/roleframe/design artifacts plus dashboard HTML.

### Test D3: The skill pushes back on the vague brief and asks for a concrete boundary.

**Input:** `/roleframe design Smart assistant for our company`

**Expected behavior:**
- [ ] The response does not accept the vague request as-is.
- [ ] The response asks what specific business result or owner boundary the unit must return.
- [ ] The response hints at decomposition if the user describes multiple functions.

### Test D4: A pack-profile design package with governance-first design and no parallel owner surfaces.

**Input:** `/roleframe design pack Pack for donor skill intake with explicit routes, proof surfaces, and staged rollout`

**Expected behavior:**
- [ ] The response treats the brief as a pack profile.
- [ ] The response asks about owner boundary, owned surfaces, and proof surfaces.
- [ ] The response includes routes, deployment visibility, rollout, and preparedness.
- [ ] The response avoids collapsing the pack into a single agent function.

## Mode: review

### Test R1: A full review over the legacy agent fixtures with discovery, evidence-driven findings, structured audit JSON files, rendered markdown views, and a dashboard build.

**Input:** `/roleframe review evals/files/sample-agents/agents`

**Expected behavior:**
- [ ] The response starts with discovery or inventory of unit-related artifacts in the supplied path.
- [ ] The response discovers all fixture agent files.
- [ ] The response resolves the placeholder include used by the supervisor fixture.
- [ ] The response cites concrete file paths or file:line evidence.
- [ ] The response includes cross-unit analysis or overlap findings.
- [ ] The response creates or clearly intends structured audit JSON, rendered markdown views, and dashboard HTML as review artifacts.

### Test R2: The skill uses project-root discovery when no path argument is supplied.

**Input:** `/roleframe review`

**Expected behavior:**
- [ ] The response mentions discovery from the project root or default project search.
- [ ] The response stays in review mode.
- [ ] The response does not require a path before it can explain the workflow.

### Test R3: The skill reviews a single agent-profile unit deeply, still using discovery for related assets and still producing review artifacts.

**Input:** `/roleframe review agent evals/files/sample-agents/agents/supervisor.md`

**Expected behavior:**
- [ ] The response scopes the review to the supplied file.
- [ ] The response still discovers related prompt, tool, or runtime assets.
- [ ] The response still applies the audit structure.
- [ ] The response still treats review as an artifact-producing workflow rather than a one-off text critique.

### Test R4: A pack-aware review over manifest, route, proof, rollout, and prompt artifacts with structured review output.

**Input:** `/roleframe review pack evals/files/sample-pack`

**Expected behavior:**
- [ ] The response starts with artifact inventory rather than prompt-only archaeology.
- [ ] The response discovers manifest, route, tests, and proof surfaces.
- [ ] The response uses manifest or proof evidence, not prompt evidence alone.
- [ ] The response includes governance findings about owner boundary, route contract, visibility, or preparedness.
- [ ] The response creates or clearly intends structured audit JSON, rendered markdown views, and dashboard HTML under docs/roleframe/review.

### Test R5: A mixed-profile review that discovers both agent and pack signals and applies profile-aware analysis.

**Input:** `/roleframe review evals/files/sample-mixed`

**Expected behavior:**
- [ ] The response discovers both agent and pack artifacts.
- [ ] The response applies profile-aware framing instead of one universal prompt-archeology pass.
- [ ] The response mentions route or contract matrix implications across profiles.
- [ ] The response still produces structured review artifacts.

## Eval workflow checks

- Before grading `design`, verify the raw response, design markdown files, summary, and `dashboard.html`.
- Before grading `review`, verify the raw response, audit markdown files, summary, and `dashboard.html`.
- Run the first wave before the second wave in the risk-based cycle.
