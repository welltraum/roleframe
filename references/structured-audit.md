# Structured audit package

## Canonical source of truth

RoleFrame review is JSON-first.

Canonical files:

- `docs/roleframe/review/NN_name.audit.json`
- `docs/roleframe/review/summary.audit.json`

Derived views:

- `docs/roleframe/review/NN_name.md`
- `docs/roleframe/review/README.md`
- `docs/roleframe/review/dashboard.html`

Legacy `docs/agent_audit/*` is compatibility-only.

Project-local profiles may place derived review outputs in repo diagnostics surfaces. That does not change the JSON schema or make the derived output canonical truth.

## Required schema for `NN_name.audit.json`

Top-level keys:

- `metadata`
- `summary`
- `artifact_inventory`
- `idef0`
- `governance`
- `criteria`
- `evidence_points`
- `contracts`
- `anti_patterns`
- `backlog`
- `patch_plan`

### `metadata`

Required:

- `name`
- `unit_kind`
- `language`
- `source_files`
- `reviewed_at`

### `artifact_inventory`

3-10 items. Each item must contain:

- `type`
- `path`
- `role`

Allowed `type` values:

- `prompt`
- `manifest`
- `route`
- `runtime`
- `test`
- `proof_surface`
- `doc`

### `governance`

Required:

- `owner_boundary`
- `route_matrix`
- `proof_surfaces`
- `deployment_visibility`
- `rollout`
- `preparedness`

`route_matrix` is a non-empty list of objects with:

- `source`
- `target`
- `status`
- `note`

### `criteria`

Exactly 10 items, using the canonical criterion keys for compatibility.

Criterion `business_boundary` is profile-aware:

- `agent`: atomic business function
- `pack`: ownership boundary
- `workflow`: decomposition and orchestration boundary

## Required schema for `summary.audit.json`

Required keys:

- `language`
- `title`
- `subtitle`
- `overall_verdict`
- `overview_cards`
- `canonical_findings`
- `architecture`
- `critical_issues`
- `maturity_matrix`
- `contract_matrix`
- `roadmap`
- `agents_lead`

Visible text should use unit vocabulary even though the key remains for compatibility.

## Field budgets

| Field | Budget |
|---|---|
| `summary.verdict` | 2-4 sentences |
| `artifact_inventory` | 3-10 items |
| `evidence_points` | 3-5 items |
| `anti_patterns` | 1-6 items |
| `backlog` | 3-6 rows |
| `patch_plan` | exactly 3 items |

## What the LLM fills

- evidence-backed judgments
- IDEF0 reconstruction
- governance reconstruction
- criterion scores
- contract diffs
- backlog
- patch plan

It does not hand-write HTML.
