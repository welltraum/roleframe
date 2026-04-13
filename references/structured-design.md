# Structured design package

## Canonical source of truth

RoleFrame design is JSON-first.

Canonical files:

- `docs/roleframe/design/NN_name.design.json`
- `docs/roleframe/design/summary.design.json`

Derived views:

- `docs/roleframe/design/NN_name.md`
- `docs/roleframe/design/README.md`
- `docs/roleframe/design/dashboard.html`

Legacy `docs/agent_design/*` is compatibility-only.

If a project-local profile remaps output placement, it must preserve this schema and treat the mapped files as a projection of the same design package.

## Required schema for `NN_name.design.json`

Top-level keys:

- `metadata`
- `summary`
- `business_function`
- `idef0`
- `control_spec`
- `mechanism_spec`
- `governance`
- `contracts`
- `dependencies`
- `evaluation_plan`
- `delivery_plan`

### `metadata`

Required:

- `name`
- `unit_kind`
- `language`
- `source_context`
- `designed_at`

`unit_kind` must be `agent`, `pack`, or `workflow`.

### `business_function`

Keep the key name for compatibility, but interpret it by profile:

- `agent`: business function boundary
- `pack`: ownership boundary
- `workflow`: orchestration boundary

Required:

- `goal`
- `consumer`
- `success_criteria`
- `in_scope`
- `out_of_scope`

### `governance`

Required:

- `owner_boundary`
- `routes`
- `owned_surfaces`
- `proof_surfaces`
- `deployment_visibility`
- `rollout`
- `preparedness`

`routes` is a non-empty list of objects with:

- `name`
- `consumer`
- `contract`
- `risk`

## Required schema for `summary.design.json`

Required keys:

- `language`
- `title`
- `subtitle`
- `overall_verdict`
- `overview_cards`
- `architecture`
- `critical_risks`
- `contract_matrix`
- `implementation_phases`
- `agents_lead`

The key `agents_lead` is still accepted for compatibility, but the visible text should talk about units.

## Field budgets

| Field | Budget |
|---|---|
| `summary.verdict` | 2-4 sentences |
| `idef0.*` | 1-2 sentences |
| `control_spec.sop` | 3-7 steps |
| `governance.routes` | 1-6 rows |
| `dependencies` | 1-6 rows |
| `implementation_phases` | 2-5 rows |

## Design intent

The LLM fills semantics only:

- boundary
- Control vs Mechanism
- governance
- contracts
- eval and delivery

The renderer handles markdown and dashboard composition.
