# roleframe

RoleFrame is an Agent Skill for designing, auditing, and explaining AI agent systems through the IDEF0 lens: business function, control, mechanism, output.

It is built as a public single-skill repository and reference implementation for the [Agent Skills](https://agentskills.io/home) format. The skill is tuned for Claude Code first, but the repository structure follows the portable `SKILL.md` convention and keeps large materials in `references/`, static assets in `assets/`, and reusable helpers in `scripts/`.

## Why this exists

Most agent reviews stop at prompt wording. RoleFrame treats an agent as a designed software function with explicit boundaries:

- `Input`: what starts the function
- `Control`: role, SOP, constraints, output contract
- `Mechanism`: tools, memory, runtime, model
- `Output`: typed result, empty result, failure result

That framing makes design reviews repeatable, gives audits a stable rubric, and helps teams move from "smart assistant" language to implementable architecture.

## Modes

| Command | Purpose |
|---|---|
| `/roleframe design <description>` | Design a new agent or multi-agent system as business functions |
| `/roleframe review [path]` | Audit existing agents against the RoleFrame maturity model |
| `/roleframe dashboard [path]` | Build an HTML dashboard from a structured audit package |

Russian prompts are supported directly, for example:

- `Спроектируй агента для обработки заявок`
- `Проведи аудит агентов`
- `Собери дашборд агентов`

The skill keeps output language aligned with the user request, including generated JSON, markdown, and HTML artifacts.

## Install and use

Copy this repository into a skills-compatible client as a folder named `roleframe`.

Examples:

```bash
# Claude Code, project-level
cp -R roleframe /path/to/project/.claude/skills/

# Claude Code, user-level
cp -R roleframe ~/.claude/skills/

# OpenAI Codex-compatible agents
cp -R roleframe /path/to/project/.agents/skills/
```

Then invoke it explicitly with `/roleframe ...` or let the client auto-activate it from the description.

## Repository layout

```text
roleframe/
├── SKILL.md
├── README.md
├── LICENSE
├── .github/workflows/validate.yml
├── assets/
│   └── dashboard-template.html
├── references/
│   ├── anti-patterns.md
│   ├── audit-template.md
│   ├── checklist.md
│   ├── dashboard-playbook.md
│   ├── methodology.md
│   ├── passport-template.md
│   ├── prompt-archaeology.md
│   └── structured-audit.md
├── evals/
│   ├── evals.json
│   ├── expected-findings.md
│   ├── functional-tests.md
│   ├── grading-rubric.md
│   ├── performance-comparison.md
│   ├── review-dashboard-runbook.md
│   ├── trigger-tests.md
│   └── files/
│       ├── sample-agents/
│       └── sample-audits/
├── scripts/
│   ├── benchmark_eval.py
│   ├── check_eval_artifacts.py
│   ├── prepare_eval.py
│   ├── render_audit_package.py
│   ├── render_eval_docs.py
│   └── validate_skill.py
└── eval-workspace/
```

## Evaluation workflow

The canonical eval source is `evals/evals.json`. The markdown files in `evals/` are generated human-readable views and should be refreshed from that source.

Recommended loop:

```bash
# 1. Structural validation with workspace-local uv caches
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/validate_skill.py --skip-skills-ref

# 2. Refresh generated eval docs if evals.json changed
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/render_eval_docs.py

# 3. Prepare a clean iteration workspace
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/prepare_eval.py --iteration 1 --wave 1

# 4. Run fresh with-skill / without-skill sessions in Codex
#    and save outputs into eval-workspace/iteration-1/.../outputs
#    Raw response goes to outputs/response.md

# 5. Verify required artifacts and content checks before grading
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/check_eval_artifacts.py --iteration-dir eval-workspace/iteration-1

# 6. Replace pending grading.json and timing.json templates, then aggregate
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/benchmark_eval.py --iteration-dir eval-workspace/iteration-1
```

Canonical review/dashboard runbook:

- [`evals/review-dashboard-runbook.md`](evals/review-dashboard-runbook.md)
- [`evals/expected-findings.md`](evals/expected-findings.md)

Evaluation follows the [Agent Skills guidance on structured evals](https://agentskills.io/skill-creation/evaluating-skills):

- trigger cases
- functional cases
- with-skill vs without-skill comparison
- timing and token capture
- assertion grading
- human blind review for qualitative differences
- artifact completeness before grading
- fast-model plus reasoning-model spot checks for regression drift

First-cycle release work uses a risk-based order:

- wave 1: all trigger cases, `functional-design-d1`, `functional-design-d3`, `functional-review-r1`,
  `functional-dashboard-b1`, `functional-dashboard-b2`, and `comparison-b`
- wave 2: the remaining functional and comparison cases after wave 1 is healthy

## Validation

Use the official reference validator plus the repository checks:

```bash
uvx --from git+https://github.com/agentskills/agentskills#subdirectory=skills-ref \
  skills-ref validate .

uv run scripts/validate_skill.py --skip-skills-ref
```

The custom validator checks:

- frontmatter presence and required fields
- `name` consistency with the directory name
- approximate token budget for `SKILL.md`
- broken relative links from `SKILL.md` and `references/*.md`
- shape of `evals/evals.json`
- generated eval docs are in sync with `evals/evals.json`

The structured audit renderer validates:

- `*.audit.json` schema completeness
- 10 canonical maturity criteria
- evidence presence
- current/target contracts
- backlog and top-3 patch plan

Example:

```bash
uv run scripts/render_audit_package.py --input evals/files/sample-audits --output /tmp/roleframe-audit --check
```

`scripts/check_eval_artifacts.py` verifies the manual eval outputs that the benchmark depends on:

- raw response export
- structured audit package plus markdown views for `review`
- `dashboard.html` for `review` and `dashboard`
- minimal content signals such as evidence references, schema presence, and dense dashboard blocks

## Release policy

`v0.3.0` is considered releasable only when all of the following are true:

- `skills-ref validate .` passes
- `uv run scripts/validate_skill.py` passes
- curated trigger and functional evals are green
- benchmark output exists for the current iteration
- install instructions work from a clean machine

## License

This repository uses [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
