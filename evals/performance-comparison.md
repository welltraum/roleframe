# Performance Comparison: With vs Without Skill

## Baseline (without /roleframe)

Ask Claude to audit agents or design a new agent without the skill loaded.

### Typical baseline behavior

| Aspect | Without skill |
|---|---|
| Methodology | Ad-hoc, inconsistent between runs |
| IDEF0 model | Not used unless user explicitly asks |
| Criteria scoring | No standard rubric, subjective |
| Output contract coverage | Happy path only, no empty/error paths |
| Checklist | None -- items vary per run |
| File-level recommendations | Vague ("improve the prompt") |
| Dashboard | Generic HTML without methodology structure |
| Cross-agent analysis | Usually skipped |
| Consistency across runs | Low -- different structure each time |

## Expected improvement (with /roleframe)

| Aspect | With skill | Improvement |
|---|---|---|
| Methodology | IDEF0-based, consistent | Repeatable framework |
| IDEF0 model | Always applied, 4 quadrants | Structural completeness |
| Criteria scoring | 10 criteria, 0-3 scale, rubric | Objective measurement |
| Output contract | 3 paths: happy + empty + error | Robustness |
| Checklist | 14 items, mapped to IDEF0 | No gaps |
| File-level recommendations | Concrete file:line references | Actionable |
| Dashboard | Pre-built template, 3 views | Professional output |
| Cross-agent analysis | Overlaps, routing, dead links | System-level view |
| Consistency across runs | High -- same structure every time | Reliability |

## How to measure

### Test A: Agent design comparison

1. **Without skill:** Ask Claude "Design an agent for processing product return requests"
2. **With skill:** `/roleframe design Agent for processing product return requests`
3. Compare outputs on:
   - [ ] IDEF0 card present and complete?
   - [ ] Output contract covers 3 paths?
   - [ ] Checklist applied?
   - [ ] Decomposition suggested if needed?
   - [ ] Control vs Mechanism explicitly separated?

### Test B: Agent review comparison

1. **Without skill:** Ask Claude "Review the agent in agents/1c/supervisor.md"
2. **With skill:** `/roleframe review agents/1c/supervisor.md`
3. Compare outputs on:
   - [ ] Standard audit structure (12 sections)?
   - [ ] 10 criteria scored with rubric?
   - [ ] Backlog with file:line references?
   - [ ] Cross-agent findings?

### Test C: Dashboard comparison

1. **Without skill:** Ask Claude "Create an HTML dashboard for the agent audit in docs/agent_audit/"
2. **With skill:** `/roleframe dashboard`
3. Compare outputs on:
   - [ ] Uses pre-built template structure?
   - [ ] Three switchable views?
   - [ ] Mermaid architecture diagram?
   - [ ] Checklist summary table?
   - [ ] File:line references in issues?

## Results log

| Test | Without skill (notes) | With skill (notes) | Improvement? |
|---|---|---|---|
| A | | | |
| B | | | |
| C | | | |
