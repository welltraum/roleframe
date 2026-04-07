# RoleFrame Methodology Reference

## Foundation

An agent is NOT a "smart chat". It is a **designed software function** with explicit boundaries, rules, tools, execution cycle, and measurable quality.

The minimal unit of design is a **single business function**. "Universal assistant" is almost always a bad starting point -- it signals the need for decomposition into roles, processes, and sub-agents.

**Wrong framing:** "Build a smart assistant that helps employees."
**Right framing:** "Design an agent that transforms a fuzzy user request into a valid structured query to the product catalog."

## Two complementary engineering loops

| Loop | Responsibility | Typical outputs |
|---|---|---|
| **Engineering** | Architecture, runtime, memory, integrations, CI/CD, monitoring, guardrails | Service, contracts, environments, logging, SLA |
| **Research** | Role, SOP, constraints, prompt design, experiments, evaluation | Prompt versions, datasets, metrics, regression sets |

**Mistake #1:** Trying to solve everything with code only -> formally correct but useless agent.
**Mistake #2:** Trying to solve everything with prompts only -> fast but unmanageable prototype.

## IDEF0: Four quadrants of an agent function

```
         Control
    (role, SOP, constraints,
     output contract)
            |
            v
Input ---> [FUNCTION] ---> Output
            ^
            |
        Mechanism
    (tools, memory, runtime, LLM)
```

| Quadrant | Contains | Examples |
|---|---|---|
| **Input** | Data that triggers the function | User request, files, dialog state, history |
| **Control** | Rules constraining behavior. **Skill/system prompt = Control** | Role, SOP, constraints, output contract, decision tables |
| **Mechanism** | Resources enabling execution | Tools, MCP servers, memory, LLM, runtime loop, middleware |
| **Output** | Result with a defined contract | Structured JSON, delegation, question to user |

### Key principle: Skill = Control

The system prompt, instructions, and SOP ARE the Control component in IDEF0 terms. When designing or auditing, always explicitly separate:
- **Control** (rules, prompts, constraints) -- what the agent MUST and MUST NOT do
- **Mechanism** (tools, code, runtime) -- HOW the agent does it

IDEF0 is used for one function at a time. Do not try to pack the entire platform into one diagram.

## 10 maturity criteria

Each criterion is scored 0-3:
- **0** -- absent
- **1** -- present implicitly or fragmentarily
- **2** -- formulated and partially implemented
- **3** -- fully described, implemented, and verified

| # | Criterion | What to check | Typical risk when low |
|---|---|---|---|
| 1 | Business boundary | Explicit function description and responsibility zone | Agent tries to do everything |
| 2 | Input definition | Allowed inputs, request classes, edge cases | Random misses on real queries |
| 3 | Control layer | Role, SOP, constraints, output contract exist | Unstable behavior, hallucinations |
| 4 | Mechanism layer | Tools, their rights, invocation method are clear | Erroneous or excessive tool calls |
| 5 | Context engineering | Static/dynamic context separated, selection rules exist | Context stuffing, latency, cost |
| 6 | Runtime loop | Orchestrator, step limits, error handling | Loops, silent failures |
| 7 | Evaluation | Dataset, metrics, negative scenarios | Quality cannot be proven |
| 8 | Observability | Logs, tracing, cost/latency monitoring | Cannot localize defects |
| 9 | Safety | Guardrails, permission limits, honest failure modes | Unpredictable damage |
| 10 | Change management | Prompts versioned, regressions tracked | Breaking prod with words |

### Score interpretation

| Range | Level | Description |
|---|---|---|
| **0-10** | Experiment | No engineering foundation |
| **11-20** | Working prototype | Has basics but gaps remain |
| **21-25** | Managed agent | Controlled and measurable |
| **26-30** | Mature component | Platform-ready |

## 8 design steps

1. **Fix responsibility boundary** -- what business result, who is the consumer, where does responsibility end
2. **Extract minimal business function** -- decompose if too broad
3. **Gather requirements via IDEF0** -- input, control, mechanism, output for each function
4. **Design behavior control** -- role, SOP, constraints, output contract (answers: what does agent do, how, what must it NOT do)
5. **Design execution** -- tools, tool selection rules, static/dynamic context, memory, step limits, batching, error handling
6. **Design evaluation before production** -- scenario classes, negative/edge cases, tool mocks, proxy metrics, regression runs
7. **Package for operations** -- logging of inputs, tool calls, output contract, rejection reasons, latency, cost, fallback behavior
8. **Introduce evolution cycle** -- every significant change to prompt/SOP/tool orchestration goes through re-evaluation and regression

## Correction priority order (from highest risk to lowest)

1. Fix function and output contract
2. Describe role, SOP, constraints
3. Fix tools, memory, runtime loop
4. Build evaluation dataset and regression
5. Only then optimize cost, quality, and UX

## Required design artifacts

| Artifact | Contents | Owner | Purpose |
|---|---|---|---|
| Agent passport | Name, goal, user, in-scope/out-of-scope, inputs, outputs, criticality | PO/BA | Overall solution frame |
| IDEF0 function | Input, Control, Mechanism, Output | BA/SA | Boundaries and dependencies |
| Behavioral spec | Role, SOP, constraints, output contract | AI Engineer | Controlling stochastic behavior |
| Runtime design | Context, memory, tools, step cycle, limits | Backend/Arch | Managed execution |
| Evaluation pack | Dataset, metrics, mocks, regression | AI Eng/QA | Measurable quality |
| Operational pack | Logs, tracing, alerts, degradations, fallbacks | DevOps/SRE | Production support |

## Diagram notation guide

| Notation | When to use | What it captures |
|---|---|---|
| IDEF0 | Designing an agent function | Boundaries: input, control, mechanism, output |
| BPMN | Describing SOP and process branches | Step order, forks, hand-offs, errors |
| Sequence | Showing runtime and entity interactions | Who sends what to whom and in what order |
| C4-lite / container | Discussing service architecture | Components, integrations, responsibilities |
| Decision table | Many rules and exceptions | Condition combinations and allowed actions |

## Symptom-to-fix mapping

| Symptom | Probable root cause | First action |
|---|---|---|
| Agent "over-answers" | No clear function and role model | Narrow responsibility, rewrite identity & goal |
| Chaotic tool calls | Implicit SOP, no orchestration | Explicitly describe call order and IF/ELSE conditions |
| Output hard to use programmatically | No output contract | Introduce strict output JSON and validation |
| Slow and expensive | Context stuffing, excess tools | Separate static/dynamic context, reduce top-N tools |
| Errors not reproducible | No dataset and logs | Build evaluation pack and minimal tracing |
| One agent does everything | Missing decomposition | Split into functions or supervisor + sub-agents |
| Changes break everything | No change management | Version prompts, run regression |

## Project launch iterations

| Iteration | Goal | Result |
|---|---|---|
| 1 | Agent landscape inventory | Agent list, owners, criticality, symptoms, baseline maturity audit |
| 2 | Normalize design artifacts | For priority agents: passport, IDEF0, control layer, output contract |
| 3 | Stabilize execution | Tools, context management, loop limits, error handling, observability |
| 4 | Introduce quality evaluation into change cycle | Dataset, regression, rule: every edit goes through re-evaluation |
