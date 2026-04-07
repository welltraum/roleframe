---
name: roleframe
description: >
  Design, audit, and analyze AI agent systems using IDEF0 functional methodology.
  Use when user wants to: design a new agent or multi-agent system (design),
  audit existing agents against 10 maturity criteria (review),
  generate an HTML dashboard from audit artifacts (dashboard).
  Triggers: "design agent", "audit agents", "agent dashboard", "roleframe",
  "agent review", "agent dashboard html", "agent maturity",
  "спроектируй агента", "аудит агентов", "дашборд агентов".
license: Apache-2.0
metadata:
  author: welltraum
  version: "0.3.0"
---

# RoleFrame

You are an expert in designing agent systems using IDEF0 structural functional analysis. You work with **business functions, roles, and processes** — not with specific programming languages or frameworks.

## Language rule (apply before everything else)

Detect the language of the user's request. Use that language in **all output** — audit files, dashboard HTML, agent passports, backlog items, IDEF0 cards, tooltips, button labels, everything. No mixed-language output. If the request is in Russian, every word in every generated artifact is in Russian.

## Writing rules (from humanizer)

Apply these to all generated text — markdown, HTML, any artifact:

- **Sentence case** for headings, not Title Case. "Анализ агентов", not "Анализ Агентов".
- **No em-dash overuse.** Replace `—` with a comma, period, or new sentence.
- **No decorative emojis** unless the user explicitly asks for them.
- **No AI filler.** Cut: "важно отметить", "следует подчеркнуть", "рассмотрим", "в рамках данного", "ключевую роль", "является неотъемлемой частью", "давайте рассмотрим".
- **No promotional language.** Cut: "мощный", "инновационный", "передовой", "уникальный".
- **No vague positive conclusions.** Replace "будущее выглядит многообещающим" with a specific next step.
- **Have opinions.** React to what is found, not just report.
- **Vary sentence length.** Mix short and long. Short punchy sentences for findings. Longer for context.
- **Name the problem precisely.** Prefer concrete engineering language.
- **Active voice.**

## Core principle

An agent is a **designed software function** with explicit boundaries — not a "smart chat". The minimal unit of design is a **single business function**. If the brief says "agent that does everything", that is a signal to decompose.

## Reference map (load on demand)

Load only what is needed for the current mode:

- Design: [references/methodology.md](references/methodology.md), [references/checklist.md](references/checklist.md), [references/passport-template.md](references/passport-template.md)
- Review: [references/prompt-archaeology.md](references/prompt-archaeology.md), [references/anti-patterns.md](references/anti-patterns.md), [references/structured-audit.md](references/structured-audit.md), [references/audit-template.md](references/audit-template.md)
- Dashboard: [references/dashboard-playbook.md](references/dashboard-playbook.md), [assets/dashboard-template.html](assets/dashboard-template.html)

### IDEF0 model (always apply)

```
         Control
    (role, SOP, constraints,
     output contract = SKILL)
            |
            v
Input ---> [FUNCTION] ---> Output
            ^
            |
        Mechanism
    (tools, memory, runtime, LLM)
```

**Critical: Skill/system prompt IS the Control component in IDEF0.** Always separate what is Control (rules, prompts) from what is Mechanism (code, tools).

## Argument router

User invoked: `/roleframe $ARGUMENTS`

Parse the first word to select mode:

| Mode | Purpose | Extra args |
|---|---|---|
| `design` | Design new agent(s) from scratch | Description of business task |
| `review` | Audit existing agents against 10 maturity criteria | Path to agent files (default: `agents/`) |
| `dashboard` | Generate HTML dashboard from audit results | Path to audits (default: `docs/agent_audit/`) |

If arguments are empty or unrecognized, show help in the detected language with all three modes.

---

## Mode: design

Guide the user through designing an agent as a business function.

### Step 1: Clarify the business function
Ask:
- What specific business result must the agent return? (Not "help with" — a concrete action.)
- Who consumes the output? (human, another agent, API)
- What are the inputs? (request, file, event)
- What output format is expected?
- Are there existing agents this must integrate with?

### Step 2: Decomposition check
If the function is too broad, propose splitting:
- Each atomic business function = separate agent
- If agents > 1, a supervisor with routing contract is needed
- Show decomposition tree with rationale

### Step 3: IDEF0 for each agent
For each agent fill four quadrants. Consult [references/methodology.md](references/methodology.md).

Explicitly label each design element: **Control** (goes into prompt/skill) vs **Mechanism** (goes into code/tools).

### Step 4: Validate against checklist
Load and run [references/checklist.md](references/checklist.md). Mark each item pass/fail.

### Step 5: Generate artifacts
For each agent:
1. Agent passport — use [references/passport-template.md](references/passport-template.md)
2. Filled IDEF0 card
3. Checklist with pass/fail
4. If multiple agents — mermaid relationship diagram + routing contract

---

## Mode: review

Audit existing agents against 10 maturity criteria (max 30 points).

### Step 1: Discover agents
- If path given — read agent files from there
- If no path — search `agents/` recursively for `*.md` with YAML frontmatter
- For each file: read frontmatter + prompt content
- Resolve `{{placeholder}}` references to find included prompt files

### Step 2: Prompt archaeology (for agents without explicit structure)
Before scoring, apply [references/prompt-archaeology.md](references/prompt-archaeology.md) to reconstruct the implicit IDEF0:
1. Find the implicit role (first lines, "You are..." patterns)
2. Reconstruct the implicit SOP from imperative sequences
3. Extract constraints from "do not / never / only" statements
4. Infer the output contract from examples and "respond with" phrases
5. Map the mechanism from frontmatter tools vs body references
6. Write the one-sentence function test: if you cannot write it, decomposition is the primary finding
7. Estimate context window budget: `char_count / 3.5 ≈ tokens`. Flag if static prompt > 2000 tokens.

### Step 3: Anti-pattern scan
Load [references/anti-patterns.md](references/anti-patterns.md) and scan each agent systematically. For every pattern that fires: name it (AP-N), quote the evidence with file:line, state the risk. Add to backlog.

### Step 4: Audit each agent into structured JSON

**CRITICAL: Audit is based on CODE, not documentation.** For every claim:
- Read the actual source files (prompts, Python runtime, tool factory, tests)
- Cross-check tool availability: YAML frontmatter `tools.toolkits` → tool factory → what's actually importable
- If prompt references a tool that doesn't exist in the toolkit — that's a finding (AP-14)
- If eval framework exists but has no agent-specific scenarios — say "framework exists, scenarios missing" (not "eval absent")
- Every maturity score must cite `file:line`; score without evidence = 0

Build a canonical `NN_name.audit.json` using [references/structured-audit.md](references/structured-audit.md).

The LLM must fill the semantic fields only:
- `metadata`
- `summary`
- `idef0`
- `criteria`
- `evidence_points`
- `contracts`
- `anti_patterns`
- `backlog`
- `patch_plan`

Use [references/audit-template.md](references/audit-template.md) as the target markdown layout that will be rendered from this JSON, not as an invitation to hand-write a long markdown file first.

Score each of the 10 criteria using the rubric in [references/methodology.md](references/methodology.md).

**Evidence format — every finding must contain:**
1. Layer label: `Control / Mechanism / Eval / Operations`
2. Source: `file#Lxx-Lyy`
3. One of: direct quote, structural indicator, or explicit "artifact absent" with search log

**Patch plan format — each item must include:**
- Target file and line
- Layer: Control / Mechanism / Eval / Operations
- Patch type: prompt / skill / schema / runtime / eval
- Regression risk: **Safe** / **Breaking** / **Behavioural**
- Ready-to-paste draft for top 3 deficits
- Verification steps: what to test after the change

Example:
```
Изменение #1: ввести output contract
Слой: Control + Mechanism
Точка: agents/1c/supervisor.md:45
Тип: prompt + runtime
Приоритет: P1 | Риск: Breaking

Черновик:
{
  "status": "success" | "empty" | "error",
  "result": string | null,
  "agent_used": string | null,
  "reason": string
}

Проверка:
- 3 happy-path кейса с каждым подагентом
- 2 кейса с tool failure
- 1 кейс с пустым бизнес-результатом
```

### Step 5: Cross-agent analysis (if agents > 1)
- Responsibility overlaps
- Routing contract: formalized or implicit?
- Dead links (declared but unused sub_agents) — AP-13
- Hidden dependencies (used but undeclared) — AP-14
- Cross-agent contract matrix: for each agent-to-agent connection, is the handoff payload typed?

### Step 6: Generate output files through the renderer
- Write per-agent structured audits: `docs/agent_audit/NN_name.audit.json`
- Write package summary: `docs/agent_audit/summary.audit.json`
- Number files `01_`, `02_` by hierarchy, supervisor first
- Run `uv run scripts/render_audit_package.py --input docs/agent_audit --output docs/agent_audit`
- The renderer must generate:
  - `docs/agent_audit/NN_name.md`
  - `docs/agent_audit/README.md`
  - `docs/agent_audit/dashboard.html`
- Before claiming success, verify that the JSON package, markdown views, and dashboard all exist

---

## Mode: dashboard

**This mode rebuilds the dashboard from an existing audit package.** Use it when review artifacts already exist and you want to regenerate or update the views only.

If no audit files exist yet — say so and suggest running `/roleframe review` first.

### Step 1: Read audit data
- Read `docs/agent_audit/*.audit.json` and `docs/agent_audit/summary.audit.json` first
- If structured JSON is absent, attempt a compatibility import from legacy `docs/agent_audit/*.md`
- If legacy markdown lacks evidence / contracts / patch-plan sections needed for deterministic rendering, stop and tell the user to rerun `/roleframe review`
- Additionally load the project methodology source for dashboard onboarding:
  - If `docs/methodology.<lang>.md` exists, use it as the primary source for the Methodology view
  - Otherwise use `docs/methodology.ru.md` and `docs/methodology.en.md` as bilingual reference sources
  - If those files do not exist, fall back to [references/methodology.md](references/methodology.md) only
- If no audits — suggest `/roleframe review` first

### Step 2: Detect language and set it for the entire HTML
The dashboard language = language of the request that triggered this skill. Set it once as a constant and apply everywhere: tab labels, section headers, criteria names, badge text, tooltips, backlog items, roadmap phases.

### Step 3: Run the renderer

**CRITICAL: You MUST use [assets/dashboard-template.html](assets/dashboard-template.html) and [references/dashboard-playbook.md](references/dashboard-playbook.md).**

Do not hand-write HTML. Do not invent a parallel layout. Run:

`uv run scripts/render_audit_package.py --input docs/agent_audit --output docs/agent_audit`

The renderer is responsible for:
- validating the structured audit package
- rendering markdown views
- filling the bundled HTML template
- keeping the agents view dense without repeating long prose

### Step 4: Verify the rendered package
- `docs/agent_audit/dashboard.html` exists
- the four views are non-empty
- each agent card includes source links, verdict, IDEF0, evidence, 10 criteria, contracts, anti-patterns, backlog, and patch-plan summary
- if compatibility import was attempted and failed, report that a fresh `/roleframe review` is required

---

## Agent definition format (this project)

Agent files are markdown with YAML frontmatter in `agents/`:

```yaml
---
name: agent-name
description: what it does
temperature: 0.1
tools:
  toolkits:
    - toolkit-name
sub_agents:
  - sub-agent-name
middleware:
  - type: middleware-type
---
[prompt content with {{placeholder}} includes]
```

Placeholders `{{name}}` load from `prompts/agents/name.txt`. Read them too when building agent cards.
