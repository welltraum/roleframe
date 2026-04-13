# Dashboard playbook

## Input contract

The renderer reads structured packages:

- `NN_name.audit.json`
- `summary.audit.json`
- `NN_name.design.json`
- `summary.design.json`

Canonical location for new outputs:

- `docs/roleframe/review/*`
- `docs/roleframe/design/*`

It writes derived views only:

- `NN_name.md`
- `README.md`
- `dashboard.html`

## Renderer workflow

1. Validate every structured file.
2. Validate the matching summary.
3. Render markdown views from JSON.
4. Fill `assets/dashboard-template.html`.
5. Fail if a required block is missing.

## Mapping rules

| Dashboard area | Source |
|---|---|
| Overview | summary JSON |
| Methodology | summary JSON or renderer defaults |
| Unit cards | per-unit JSON |
| Critical issues | summary JSON |
| Matrices | summary JSON |
| Roadmap | summary JSON |

## Unit card order

Review card order:

1. source links
2. verdict
3. artifact inventory
4. IDEF0
5. governance
6. evidence
7. criteria
8. contracts
9. anti-patterns
10. backlog
11. patch plan

Design card order:

1. source links
2. verdict
3. boundary
4. IDEF0
5. control
6. mechanism
7. governance
8. contracts
9. dependencies
10. evaluation
11. delivery

## Non-negotiable rules

- dashboard HTML is derived
- `file:line` evidence must never be dropped
- governance blocks must never be omitted
- if JSON is missing required fields, the renderer must fail instead of guessing
