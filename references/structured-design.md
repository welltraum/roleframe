# Structured design package

## Quick map

- Canonical files
- Required schema
- Field budgets
- Design intent

## Canonical source of truth

RoleFrame design is **JSON-first**.

The canonical design package contains:

- `docs/agent_design/NN_name.design.json`
- `docs/agent_design/summary.design.json`

Derived views:

- `docs/agent_design/NN_name.md`
- `docs/agent_design/README.md`
- `docs/agent_design/dashboard.html`

Markdown and HTML are rendered views. They are not the source of truth.

## Required schema for `NN_name.design.json`

Top-level keys:

- `metadata`
- `summary`
- `business_function`
- `idef0`
- `control_spec`
- `mechanism_spec`
- `contracts`
- `dependencies`
- `evaluation_plan`
- `delivery_plan`

### `metadata`

Required fields:

- `name`
- `language`
- `source_context`
- `designed_at`

### `summary`

Required fields:

- `readiness_score`
- `readiness_level`
- `verdict`
- `primary_risk`

Rules:

- `readiness_score` is `0..100`
- `verdict` stays compact, 2-4 sentences
- `primary_risk` is one engineering sentence

### `business_function`

Required fields:

- `goal`
- `consumer`
- `success_criteria`
- `in_scope`
- `out_of_scope`

Rules:

- `goal` is one concrete business function sentence
- `success_criteria`, `in_scope`, `out_of_scope` are non-empty lists

### `idef0`

Required fields:

- `input`
- `control`
- `mechanism`
- `output`

### `control_spec`

Required fields:

- `role`
- `sop`
- `constraints`

Rules:

- `sop` is an ordered non-empty list
- `constraints` is a non-empty list

### `mechanism_spec`

Required fields:

- `tools`
- `memory_strategy`
- `runtime_loop`
- `error_handling`

Rules:

- `tools` is a non-empty list of objects with `name`, `purpose`, `failure_mode`

### `contracts`

Required fields:

- `consumer`
- `input_contract`
- `output_contract`
- `failure_contract`

Rules:

- contracts should be compact enough for dashboard code blocks
- prefer pseudo-JSON or strict text templates over prose

### `dependencies`

Must contain one or more items with:

- `name`
- `type`
- `reason`
- `risk`

### `evaluation_plan`

Required fields:

- `scenarios`
- `metrics`
- `regression`

Rules:

- all fields are non-empty lists

### `delivery_plan`

Required fields:

- `phases`
- `observability`
- `change_management`

Rules:

- `phases` is a non-empty list of objects with `title`, `description`
- `observability` and `change_management` are non-empty lists

## Required schema for `summary.design.json`

Required top-level keys:

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

Optional but recommended:

- `methodology`

## Field budgets

| Field | Budget |
|---|---|
| `summary.verdict` | 2-4 sentences |
| `idef0.*` | 1-2 sentences each |
| `control_spec.sop` | 3-7 steps |
| `mechanism_spec.tools` | 1-6 rows |
| `dependencies` | 1-6 rows |
| `evaluation_plan.*` | 2-6 rows |
| `delivery_plan.phases` | 2-5 phases |
| `critical_risks` | 3-5 items |
| `overview_cards` | 3-4 cards |

## Design intent

The LLM fills only the semantic design layer:

- business boundary
- Control vs Mechanism split
- typed contracts
- dependencies
- evaluation plan
- delivery phases

The renderer handles markdown and HTML composition.
