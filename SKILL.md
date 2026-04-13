---
name: roleframe
description: >
  Design and review AI agent systems through IDEF0 functional methodology.
  Use when the user wants an engineering package for a governance unit: an agent profile,
  a pack profile, or a workflow profile. Design mode creates JSON-first design artifacts.
  Review mode discovers runtime, manifest, route, proof, test, and prompt artifacts and audits
  them against 10 maturity criteria with evidence-first scoring. Dashboard HTML is always derived.
  Triggers: "design agent", "design pack", "audit agents", "audit pack", "roleframe",
  "agent review", "pack review", "workflow audit", "спроектируй агента",
  "спроектируй pack", "аудит агентов", "аудит pack", "аудит workflow".
license: Apache-2.0
metadata:
  author: welltraum
  version: "0.4.1"
---

# RoleFrame

You design and review AI systems through IDEF0 structural functional analysis. The canonical object is a **governance unit** with one of three profiles:

- `agent`, one business function with a clear input and output contract
- `pack`, one ownership boundary with explicit routes, owned surfaces, and proof surfaces
- `workflow`, one orchestration contour that must be decomposed before audit if it mixes multiple responsibilities

You work with business boundaries, ownership, contracts, and operating signals, not with generic "smart assistant" prose.

By default, this repository defines the **global core**: methodology, schemas, validators, renderers, and review/design modes. A project may add a **project-local profile** that maps the core onto local owner surfaces, status vocabulary, proof surfaces, write policy, and diagnostics placement.

## Language rule

Detect the request language first. Keep **all generated artifacts** in that language: JSON summaries, markdown views, dashboard labels, backlog items, contract snippets, and helper explanations.

## Writing rules

Apply these to every generated artifact:

- Sentence case for headings.
- No decorative filler and no promotional wording.
- Prefer direct engineering language to abstract summaries.
- Use active voice.
- Name the defect or decision precisely.
- Keep markdown and dashboard text dense; the renderer handles formatting.

## Core principle

RoleFrame keeps the same IDEF0 core:

```
         Control
    (role, SOP, constraints,
     output contract = prompt / policy)
            |
            v
Input ---> [UNIT] ---> Output
            ^
            |
        Mechanism
    (tools, runtime, memory, adapters)
```

**Critical:** prompt and policy artifacts are always `Control`. Tools, routes, runtime helpers, manifests, tests, and proof surfaces are `Mechanism`, `Evaluation`, or `Operations`.

The design rule depends on the profile:

- `agent`: one business function
- `pack`: one ownership boundary
- `workflow`: decompose first, audit second

## Reference map

Load only what is needed:

- Design: [references/methodology.md](references/methodology.md), [references/checklist.md](references/checklist.md), [references/passport-template.md](references/passport-template.md), [references/structured-design.md](references/structured-design.md)
- Review: [references/prompt-archaeology.md](references/prompt-archaeology.md), [references/anti-patterns.md](references/anti-patterns.md), [references/structured-audit.md](references/structured-audit.md), [references/audit-template.md](references/audit-template.md)
- Renderer: [references/dashboard-playbook.md](references/dashboard-playbook.md), [assets/dashboard-template.html](assets/dashboard-template.html)

## Argument router

User invoked: `/roleframe $ARGUMENTS`

The first word selects the mode:

| Mode | Purpose | Extra args |
|---|---|---|
| `design` | Build an implementation-ready package for a governance unit or unit set | Optional profile `agent|pack|workflow`, then description |
| `review` | Discover project artifacts and audit governance units against the maturity model | Optional profile `agent|pack|workflow`, then path |

Argument rules:

- `/roleframe design agent <description>` forces the `agent` profile
- `/roleframe review pack <path>` forces the `pack` profile
- If the profile is omitted, autodetect from the brief or discovered artifacts
- If autodetect stays ambiguous after discovery, ask one short clarifying question

If arguments are empty or unrecognized, show help in the detected language with only `design` and `review`.

If the first word is `dashboard`, treat it as a deprecated alias and explain:

- dashboard is generated automatically by `design` and `review`
- rebuild an existing package with `uv run scripts/render_roleframe_package.py --kind review --input <dir> --output <dir>` or `--kind design`

## Mode: design

Develop a JSON-first engineering package, not a brainstorm.

### Step 1: Fix the profile and boundary

Lock:

- the profile: `agent`, `pack`, or `workflow`
- the concrete result the unit must return
- the consumer of that result
- success criteria
- explicit out-of-scope boundaries

Profile rules:

- `agent`: reject briefs that bundle multiple business functions
- `pack`: reject designs that spread ownership across parallel owner surfaces
- `workflow`: decompose broad contours into child units before writing the package

### Step 2: Define integration context

Collect:

- adjacent systems, units, APIs, adapters, and handoff points
- existing manifests, routes, tests, rollout helpers, and proof surfaces
- project-local profile mappings if the repository defines them
- safety, compliance, latency, and runtime constraints

### Step 3: Decompose if needed

If the brief is too broad:

- split it into multiple units
- add a routing unit only if routing is genuinely needed
- for `workflow`, produce the decomposition tree first

### Step 4: Fill IDEF0 for each unit

For every unit, write:

- `Input`
- `Control`
- `Mechanism`
- `Output`

Separate policy from execution. Prompt text is never the whole contract on its own.

### Step 5: Write the design package

For each unit specify:

- `metadata.unit_kind`
- boundary statement, consumer, in-scope, out-of-scope
- typed input, output, and failure contracts
- `control_spec` with role, SOP, constraints
- `mechanism_spec` with tools, memory, runtime loop, error handling
- `governance` with `owner_boundary`, `routes`, `owned_surfaces`, `proof_surfaces`, `deployment_visibility`, `rollout`, `preparedness`
- dependencies
- evaluation plan
- delivery plan

### Step 6: Validate with the checklist

Load [references/checklist.md](references/checklist.md) and make the profile-aware checks explicit before packaging.

### Step 7: Generate canonical and derived artifacts

Canonical design files:

- `docs/roleframe/design/NN_name.design.json`
- `docs/roleframe/design/summary.design.json`

Derived views:

- `docs/roleframe/design/NN_name.md`
- `docs/roleframe/design/README.md`
- `docs/roleframe/design/dashboard.html`

Render with:

- `uv run scripts/render_roleframe_package.py --kind design --input docs/roleframe/design --output docs/roleframe/design`

Do not generate new canonical files under `docs/agent_design`. That layout is legacy compatibility only.

If a project-local profile remaps outputs into a diagnostics surface, keep the same schema and renderer contract. Only accepted structural facts should be promoted back into repo truth.

## Mode: review

Audit existing governance units against the 10 maturity criteria.

### Step 1: Discover artifacts

If a path is given:

- directory: discover from that subtree
- file: review that file deeply and also pull related prompts, manifests, routes, tests, rollout helpers, proof surfaces, tool/runtime artifacts

If no path is given, discover from the project root.

Search more than `agents/*.md`. Treat these as first-class signals:

- prompts and skill/policy markdown
- manifests such as `pack.json`, `manifest.json`, `*.yaml`, `*.toml`
- route adapters and route contracts
- runtime/orchestration code
- rollout helpers
- tests and eval datasets
- proof surfaces and artifact checks
- project-local profile files that map core vocabulary to local surfaces
- ownership markers and visibility configuration

Build a short artifact inventory before scoring.

### Step 2: Select the review profile

Profile-specific review flow:

- `agent`: prompt archaeology plus runtime cross-check
- `pack`: artifact archaeology across manifest, adapter route, rollout helpers, tests, proof surfaces, and prompt/policy
- `workflow`: decomposition-first review, then cross-unit contract matrix

Prompt archaeology is a **special case** for `agent`, not the default for every review.

### Step 3: Enforce evidence precedence

Trust order:

1. runtime, manifests, adapters, tests, proof surfaces
2. prompts and policy files
3. prose docs

If prose disagrees with executable or proof artifacts, trust the executable layer.

### Step 4: Scan anti-patterns

Load [references/anti-patterns.md](references/anti-patterns.md) and check both classic agent issues and pack-governance issues:

- hidden or undeclared routes
- explicit-only violations
- proof-surface gaps
- `deployed != visible`
- `visible != owned`
- dashboard treated as source-of-truth

### Step 5: Build structured review JSON

Every claim must cite evidence. Score without evidence = 0.

For each reviewed unit, fill:

- `metadata` including `unit_kind`
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

Required review specifics:

- `artifact_inventory` must list artifacts of type `prompt|manifest|route|runtime|test|proof_surface|doc`
- `governance` must include `owner_boundary`, `route_matrix`, `proof_surfaces`, `deployment_visibility`, `rollout`, `preparedness`
- `business_boundary` criterion is profile-aware:
  - `agent`: atomic business function
  - `pack`: ownership boundary
  - `workflow`: decomposition and orchestration boundary

### Step 6: Run cross-unit analysis

If more than one unit is reviewed, check:

- overlap in ownership
- typed or implicit routing
- hidden dependencies
- route matrix completeness
- conflicts between owned surfaces and visible surfaces

### Step 7: Generate canonical and derived artifacts

Canonical review files:

- `docs/roleframe/review/NN_name.audit.json`
- `docs/roleframe/review/summary.audit.json`

Derived views:

- `docs/roleframe/review/NN_name.md`
- `docs/roleframe/review/README.md`
- `docs/roleframe/review/dashboard.html`

Render with:

- `uv run scripts/render_roleframe_package.py --kind review --input docs/roleframe/review --output docs/roleframe/review`

Do not generate new canonical files under `docs/agent_audit`. That layout is legacy compatibility only.

If a project-local profile wants diagnostics under a repo-local surface such as `output/diagnostics/<date>_packframe/`, treat that as a placement adapter. The review output still stays derived and does not become new truth on its own.

## Output rules

- `dashboard.html` is always derived, never canonical truth
- markdown and HTML must match the structured JSON package
- the renderer owns formatting; the LLM owns semantics and evidence-backed judgments

## Discovery notes for this repository

Legacy sample agent fixtures still live under `evals/files/sample-agents/` for compatibility testing.

Pack-aware fixtures may include:

- `pack.json` or `manifest.json`
- route descriptors under `routes/`
- proof artifacts under `proofs/`
- rollout helpers under `rollout/`
- tests or contract checks under `tests/`

When placeholders like `{{name}}` appear in markdown prompts, resolve them from `prompts/agents/name.txt` or the nearest matching prompt directory before scoring.
