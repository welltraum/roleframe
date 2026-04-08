# roleframe

RoleFrame is a skill for designing and reviewing AI agent systems through IDEF0:

- `Input`: what starts the function
- `Control`: role, SOP, constraints, output contract
- `Mechanism`: tools, memory, runtime, model
- `Output`: success, empty result, failure, delegation

The repository is built as a public reference implementation for the [Agent Skills](https://agentskills.io/home) format. It is written for Claude Code first, but follows the portable `SKILL.md` layout.

## What it does

RoleFrame has two main modes:

| Command | What it does |
|---|---|
| `/roleframe design <description>` | Builds an implementation-ready design package for an agent or multi-agent system |
| `/roleframe review [path]` | Finds agent artifacts in a project and audits them against the RoleFrame maturity model |

Russian prompts are supported directly:

- `Спроектируй агента для обработки заявок`
- `Изучи проект, найди всех агентов и проведи их аудит`

The skill keeps its outputs in the user's language. During both `design` and `review`, it also generates `dashboard.html`.

![RoleFrame dashboard preview](docs/dashboard.png)

## Why use it

Many agent reviews stop at prompt wording. RoleFrame treats an agent as a software function with clear boundaries. That makes reviews easier to repeat, audits easier to compare, and design work easier to turn into implementation.

## Install

Clone the repository into a skills-compatible client as `roleframe`.

```bash
# Claude Code, project-level
git clone https://github.com/welltraum/roleframe.git .claude/skills/roleframe

# Claude Code, user-level
git clone https://github.com/welltraum/roleframe.git ~/.claude/skills/roleframe

# OpenAI Codex-compatible agents
git clone https://github.com/welltraum/roleframe.git .agents/skills/roleframe
```

Then run it with `/roleframe ...` or let the client auto-activate it from the description.

## Repository layout

```text
roleframe/
├── SKILL.md
├── README.md
├── assets/        # dashboard template
├── references/    # methodology, templates, checklists
├── evals/         # eval cases, generated docs, sample files
├── scripts/       # validation, rendering, and eval helpers
└── eval-workspace/
```

## Eval workflow

`evals/evals.json` is the source of truth. Markdown files in `evals/` are generated from it.

Typical loop:

```bash
# 1. Validate the skill
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/validate_skill.py --skip-skills-ref

# 2. Regenerate eval docs if evals.json changed
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/render_eval_docs.py

# 3. Prepare a clean workspace
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/prepare_eval.py --iteration 1 --wave 1

# 4. Run with-skill / without-skill sessions manually
#    Save outputs into eval-workspace/iteration-1/.../outputs

# 5. Check required artifacts
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/check_eval_artifacts.py --iteration-dir eval-workspace/iteration-1

# 6. Fill grading.json and timing.json, then aggregate results
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
  uv run scripts/benchmark_eval.py --iteration-dir eval-workspace/iteration-1
```

Useful runbooks:

- [`evals/review-dashboard-runbook.md`](evals/review-dashboard-runbook.md)
- [`evals/expected-findings.md`](evals/expected-findings.md)

The eval setup follows the [Agent Skills guidance on structured evals](https://agentskills.io/skill-creation/evaluating-skills): trigger cases, functional cases, with-skill vs without-skill comparison, timing and token capture, grading, and artifact checks.

## Validation

Run the official validator and the local checks:

```bash
uvx --from git+https://github.com/agentskills/agentskills#subdirectory=skills-ref \
  skills-ref validate .

uv run scripts/validate_skill.py --skip-skills-ref
```

The local validator checks:

- required frontmatter
- `name` consistency with the directory name
- approximate token budget for `SKILL.md`
- broken relative links from `SKILL.md` and `references/*.md`
- `evals/evals.json`
- generated eval docs are in sync

Renderer checks cover:

- `*.audit.json` schema completeness
- `*.design.json` schema completeness
- maturity criteria
- evidence presence
- review contracts
- design delivery, eval, and runtime blocks

Examples:

```bash
uv run scripts/render_audit_package.py --input evals/files/sample-audits --output /tmp/roleframe-audit --check
uv run scripts/render_roleframe_package.py --kind review --input evals/files/sample-audits --output /tmp/roleframe-audit --check
uv run scripts/render_roleframe_package.py --kind design --input evals/files/sample-design-package --output /tmp/roleframe-design --check
```

`scripts/check_eval_artifacts.py` verifies the manual outputs that benchmarking depends on, including response exports, design or audit packages, markdown views, and `dashboard.html`.

## Release

`v0.3.0` is releasable only if all of this is true:

- `skills-ref validate .` passes
- `uv run scripts/validate_skill.py` passes
- the selected trigger and functional evals are green
- benchmark output exists for the current iteration
- install instructions work on a clean machine

## License

This repository uses [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0).
