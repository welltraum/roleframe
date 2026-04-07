# Structured audit package

## Quick map

- Canonical files
- Required schema
- Field budgets
- Evidence cardinality
- Naming rules
- What the LLM must fill

## Canonical source of truth

RoleFrame review is now **JSON-first**.

The canonical audit package contains:

- `docs/agent_audit/NN_name.audit.json`
- `docs/agent_audit/summary.audit.json`

Derived views:

- `docs/agent_audit/NN_name.md`
- `docs/agent_audit/README.md`
- `docs/agent_audit/dashboard.html`

Markdown and HTML are rendered views. They are not the source of truth.

## Required schema for `NN_name.audit.json`

Top-level keys:

- `metadata`
- `summary`
- `idef0`
- `criteria`
- `evidence_points`
- `contracts`
- `anti_patterns`
- `backlog`
- `patch_plan`

### `metadata`

Required fields:

- `name`
- `language`
- `source_files`
- `reviewed_at`

Rules:

- `source_files` must list the primary files used as evidence
- use repo-relative paths
- `language` must match the user request language

### `summary`

Required fields:

- `total_score`
- `maturity_level`
- `verdict`
- `top_deficit`

Rules:

- `total_score` = sum of the 10 maturity criteria
- `verdict` must stay at 2-4 sentences
- `top_deficit` is one short engineering statement

### `idef0`

Required fields:

- `input`
- `control`
- `mechanism`
- `output`

Rules:

- each field must be 1-2 sentences
- do not repeat the same sentence across quadrants

### `criteria`

Must contain **exactly 10** items, one per canonical maturity criterion.

Each item must contain:

- `key`
- `label`
- `score`
- `rationale`
- `evidence`

Rules:

- `score` is `0..3`
- `rationale` is exactly one short engineering sentence
- `evidence` is a non-empty list of `file:line` or `file#Lx-Ly`

### `evidence_points`

Must contain **3-5** items.

Each item must contain:

- `layer`
- `source`
- `claim`

Use this block for the strongest evidence points only. Do not dump every citation here.

### `contracts`

Required fields:

- `consumer`
- `current_contract`
- `target_contract`

Rules:

- keep both contracts compact enough for a dashboard code block
- prefer pseudo-JSON or strict text templates over prose

### `anti_patterns`

Must contain **1-6** items.

Each item must contain:

- `tag`
- `explanation`

Use stable names such as `AP-14`, `Implicit routing contract`, `Free-form output`, `Safety risk`.

### `backlog`

Must contain **3-6** items.

Each item must contain:

- `priority`
- `layer`
- `risk`
- `action`
- `file_ref`

Rules:

- one row = one concrete action
- no summaries disguised as backlog items

### `patch_plan`

Must contain **exactly 3** items.

Each item must contain:

- `title`
- `target`
- `patch_type`
- `risk`
- `draft`
- `verification`

Rules:

- `draft` is ready-to-paste
- `verification` is a non-empty checklist

## Required schema for `summary.audit.json`

Required top-level keys:

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

Optional but recommended:

- `methodology`

## Field budgets

| Field | Budget |
|---|---|
| `summary.verdict` | 2-4 sentences |
| `idef0.*` | 1-2 sentences each |
| `criteria[].rationale` | exactly 1 sentence |
| `evidence_points` | 3-5 items |
| `anti_patterns` | 1-6 items |
| `backlog` | 3-6 rows |
| `patch_plan` | exactly top-3 |
| `critical_issues` | 3-5 items |
| `overview_cards` | 3-4 cards |

These budgets exist to keep the package dense without wasting LLM tokens on duplicate prose.

## Naming rules

- file names are ordered: `01_supervisor.audit.json`, `02_document-finder.audit.json`
- `summary.audit.json` lives in the same folder
- the markdown renderer must preserve the same order

## What the LLM must fill

The LLM must fill only the semantic layer:

- evidence-backed judgments
- IDEF0 reconstruction
- criterion scores
- contract diffs
- backlog
- patch plan
- summary facts

The LLM must **not** spend tokens on:

- manual HTML composition
- repeated markdown formatting boilerplate
- rephrasing the same finding separately for markdown and dashboard

That duplication is the renderer’s job now.
