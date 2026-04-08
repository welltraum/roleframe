# Dashboard playbook

## Quick map

- Input contract
- Renderer workflow
- Template mapping
- Agent card order
- Ranking rules
- Truncation rules
- Fallback policy

## Input contract

The renderer reads one of these structured packages:

- `NN_name.audit.json`
- `summary.audit.json`
- `NN_name.design.json`
- `summary.design.json`
- `assets/dashboard-template.html`

It writes:

- `NN_name.md`
- `README.md`
- `dashboard.html`

The renderer is deterministic. The LLM does not compose HTML by hand.

## Renderer workflow

1. Validate every structured package file for the selected kind
2. Validate the matching summary file
3. Render markdown views from JSON
4. Fill `assets/dashboard-template.html`
5. Verify that all four dashboard views are non-empty

## Template mapping

Use the template placeholders only as view slots. Do not encode semantics into ad-hoc HTML.

| Placeholder group | Source |
|---|---|
| Header and tabs | `summary.audit.json` |
| Overview cards | `summary.overview_cards` |
| Architecture text + Mermaid | `summary.architecture` |
| Methodology lead and summary blocks | `summary.methodology` or renderer defaults |
| Agent cards | per-agent `*.audit.json` |
| Critical issues | `summary.critical_issues` |
| Maturity matrix | `summary.maturity_matrix` |
| Contract matrix | `summary.contract_matrix` |
| Roadmap | `summary.roadmap` |

## Agent card order

Every agent card must keep this order:

1. Source links
2. Short verdict
3. IDEF0
4. Key evidence
5. 10-criteria table
6. Current vs target contract
7. Anti-patterns / systemic risks
8. Backlog
9. Patch plan summary

If one of these blocks is missing in JSON, the renderer must fail. Silent omission makes the dashboard shallow again.

## Ranking critical issues

Critical issues should be chosen in this order:

1. system-level contract failures
2. hidden dependencies or unsafe tool behavior
3. safety failures
4. missing eval or observability that block safe rollout

Do not waste the section on local cosmetic issues.

## Contract matrix rules

Rows = source agents.  
Columns = consumer agents.

Cell statuses:

- `typed`
- `implicit`
- `absent`
- `n/a`

Each cell must carry a short note with the main engineering risk.

## What to truncate and what to keep

Safe to compress:

- long verdict prose
- repetitive explanations already visible in criteria or evidence
- large patch drafts inside overview-level sections

Never drop:

- `file:line` evidence references
- current vs target contract
- backlog rows
- top-3 patch plan
- selected maturity scores

## Fallback policy

If structured JSON exists, use it.

If JSON is absent:

1. try to import legacy markdown
2. if the markdown lacks required sections for evidence, contracts, or patch plan, stop
3. tell the user to rerun `/roleframe review` to regenerate the package in structured form

Compatibility import is transitional, not the main path.
