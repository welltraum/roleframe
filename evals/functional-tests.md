# Functional Tests

Verify that each mode produces correct, complete output.

---

## Mode: design

### Test D1: Simple single-agent design

**Input:** `/roleframe design Agent that converts a fuzzy user request into a structured query to a product catalog`

**Expected behavior:**
- [ ] Asks clarifying questions about business function, consumer, inputs, output format
- [ ] Does NOT jump to implementation before understanding the function
- [ ] Produces IDEF0 card with all 4 quadrants filled
- [ ] Explicitly labels what is Control vs Mechanism
- [ ] Generates agent passport using the template from references/passport-template.md
- [ ] Output contract covers happy path, business-empty, and tool failure
- [ ] Runs 14-point checklist and marks each item
- [ ] Proposes concrete file paths for artifacts

### Test D2: Multi-agent decomposition

**Input:** `/roleframe design System for end-to-end processing of tax authority requests: extract requirements, find documents, prepare response, archive`

**Expected behavior:**
- [ ] Recognizes the function is too broad for one agent
- [ ] Proposes decomposition into 3-4 agents with rationale
- [ ] Creates supervisor + sub-agent structure
- [ ] Generates mermaid diagram of relationships
- [ ] Defines routing contract between supervisor and sub-agents
- [ ] Each agent gets its own passport and IDEF0 card
- [ ] Boundary matrix shows no overlaps

### Test D3: Edge case -- vague request

**Input:** `/roleframe design Smart assistant for our company`

**Expected behavior:**
- [ ] Does NOT accept the vague formulation
- [ ] Pushes back: "What specific business result must the agent return?"
- [ ] Guides toward concrete business function
- [ ] Suggests decomposition if user describes multiple functions

---

## Mode: review

### Test R1: Review existing agents

**Input:** `/roleframe review agents/1c`

**Expected behavior:**
- [ ] Discovers all agent files in agents/1c/
- [ ] Reads YAML frontmatter + prompt content for each
- [ ] Resolves {{placeholder}} references to find included files
- [ ] Generates 12-section audit for each agent
- [ ] Scores all 10 criteria with justification
- [ ] Backlog items reference SPECIFIC file paths and line numbers
- [ ] Cross-agent analysis identifies responsibility overlaps
- [ ] Creates docs/agent_audit/NN_name.md files
- [ ] Creates docs/agent_audit/README.md with summary table
- [ ] Runs 14-point checklist per agent

### Test R2: Review with default path

**Input:** `/roleframe review` (no path argument)

**Expected behavior:**
- [ ] Auto-discovers agents/ directory
- [ ] Finds all agent files recursively
- [ ] Proceeds with full review

### Test R3: Review single agent

**Input:** `/roleframe review agents/1c/supervisor.md`

**Expected behavior:**
- [ ] Reviews only the specified agent
- [ ] Still produces full 12-section audit
- [ ] Still runs checklist

---

## Mode: dashboard

### Test B1: Generate dashboard from existing audits

**Input:** `/roleframe dashboard`

**Expected behavior:**
- [ ] Reads all docs/agent_audit/*.md files
- [ ] Generates self-contained HTML file
- [ ] Uses template from assets/dashboard-template.html as structural foundation
- [ ] Three views work: Overview, Agents, Issues & Roadmap
- [ ] Mermaid architecture diagram renders correctly
- [ ] Score bars show correct percentages and colors
- [ ] Agent cards show IDEF0, 10 criteria, backlog with file:line references
- [ ] Issues view shows aggregated problems ranked by risk
- [ ] Roadmap follows priority: function -> control -> mechanism -> evaluation -> operations
- [ ] Checklist summary table shows pass/partial/fail per agent
- [ ] Output file: docs/agent_audit/infographic.html
- [ ] HTML opens correctly in browser

### Test B2: Dashboard without audits

**Input:** `/roleframe dashboard` (when docs/agent_audit/ has no .md files)

**Expected behavior:**
- [ ] Detects no audit files
- [ ] Suggests running `/roleframe review` first
- [ ] Does NOT generate an empty or broken HTML

---

## Quality criteria

| Metric | Target |
|---|---|
| All 4 IDEF0 quadrants filled in every output | 100% |
| Backlog items with concrete file:line references | >80% |
| Checklist items evaluated per agent | 14/14 |
| Output contract covers 3 paths (happy, empty, error) | 100% in design mode |
| Cross-agent analysis present when agents > 1 | 100% |
| Dashboard renders without JS errors | 100% |
