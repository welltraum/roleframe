# Anti-pattern library

Detect these patterns during `review`. For each found pattern: name it, quote the evidence from the source file, explain the risk, include in backlog with regression risk label.

---

## Control layer anti-patterns

### AP-1: God Prompt
**Signature:** Single prompt file > 200 lines mixing routing logic + domain instructions + file handling + output formatting + error recovery.
**Evidence to look for:** Multiple unrelated `##` sections in one file, e.g. "## Routing", "## File processing", "## BSL rules", "## Output format" all in the same agent md.
**Risk:** Any single change cascades unpredictably. Testing one behavior requires re-testing all others.
**Fix type:** Decompose into separate policy documents or separate agents. Regression risk: **Breaking**.

### AP-2: Implicit State Machine
**Signature:** SOP described through examples ("First do X, then if Y do Z, otherwise...") rather than explicit states and transitions.
**Evidence:** Numbered lists that mix conditions with steps, e.g. "1. Try to query. 2. If no result, search docs. 3. If still nothing, ask user."
**Risk:** Behavior is unpredictable on inputs not covered by examples. Model interpolates states incorrectly.
**Fix type:** Rewrite as explicit decision table or state diagram. Regression risk: **Behavioural**.

### AP-3: Prompt as Database
**Signature:** SQL query templates, large enum lists, dictionary mappings, or static lookup tables embedded directly in the prompt.
**Evidence:** Inline JSON blobs, SQL fragments, lists of 20+ document types or field names inside the prompt text.
**Risk:** Context stuffing — static content crowds out dynamic context. Expensive. Brittle when values change.
**Fix type:** Extract to tool lookup or separate reference file loaded on demand. Regression risk: **Safe**.

### AP-4: Control-Mechanism Bleed
**Signature:** Prompt contains implementation details that belong in code: specific API endpoints, retry counts, timeout values, query syntax.
**Evidence:** `curl` commands, SQL dialect specifics, hardcoded URLs, specific error codes inside prompt instructions.
**Risk:** Prompt becomes a maintenance burden for engineers, not just AI researchers. Changes require dual updates.
**Fix type:** Move implementation details to tool descriptions or config. Keep prompt at policy level. Regression risk: **Safe**.

### AP-5: Role Identity Drift
**Signature:** Agent declares one role at the top ("You are a routing agent") but the body contradicts it with deep domain behavior ("You must also validate BSL code syntax...").
**Evidence:** Compare first 5 lines (role declaration) against the full set of capabilities described below.
**Risk:** Model identity is incoherent. Out-of-scope requests leak through because the model is uncertain about its own boundaries.
**Fix type:** Rewrite identity to match actual scope, or split into two agents. Regression risk: **Behavioural**.

---

## Output contract anti-patterns

### AP-6: Free-Form Output
**Signature:** No defined output format. Agent "returns a text response" or "answers the question."
**Evidence:** No JSON schema, no enum of return variants, no output contract section in prompt.
**Risk:** Downstream consumers cannot parse results programmatically. Integration is fragile and breaks silently.
**Fix type:** Add typed output contract with at least 3 paths (happy / empty / error). Regression risk: **Breaking** (downstream may be parsing current free-form output).

### AP-7: Happy Path Only Contract
**Signature:** Output contract exists but covers only the success case. No definition of what to return when data is absent or a tool fails.
**Evidence:** Output section describes the normal result but has no `null` / empty / error variants.
**Risk:** Agent silently hallucinates data or crashes on empty results. Graceful degradation is undefined.
**Fix type:** Add business-empty and tool-failure response variants. Regression risk: **Safe** (additive).

### AP-8: Output Contract in Prose
**Signature:** Output format described in natural language ("Return a JSON with the result") without an actual schema.
**Evidence:** Phrases like "respond with JSON containing the fields..." without a literal schema or example.
**Risk:** Model interprets field names, types, and nesting inconsistently across runs.
**Fix type:** Replace prose with a literal JSON schema or concrete example. Regression risk: **Breaking** (format may shift).

---

## Mechanism / tool anti-patterns

### AP-9: Tool Hallucination Trap
**Signature:** Tool is listed in frontmatter but prompt gives no instructions on what to do when it returns an error or empty result.
**Evidence:** Tool name appears in `tools.toolkits` but the prompt has no "if the tool fails..." or "if no results are returned..." clause.
**Risk:** On tool failure, the model invents results or loops. Silent corruption of downstream data.
**Fix type:** Add tool failure handling per tool. Regression risk: **Safe**.

### AP-10: Unbounded Tool Rights
**Signature:** Agent has access to a broad toolkit but the prompt does not restrict which tools to use in which situations.
**Evidence:** `toolkits: [common_tools, e1s_tools, python_executor, filesystem_tools]` with no usage policy in the prompt.
**Risk:** Model uses expensive or destructive tools speculatively. Side effects are unpredictable.
**Fix type:** Add explicit tool selection policy (when to use what, when NOT to use). Regression risk: **Behavioural**.

### AP-11: Python Executor Scope Creep
**Signature:** `python_executor` is available and the prompt allows arbitrary code execution without a defined scope.
**Evidence:** Prompt says "use python_executor to process files" without specifying allowed operations, output format, or safety constraints.
**Risk:** Arbitrary side effects. File system changes outside expected scope. Hard to audit.
**Fix type:** Scope to specific operation types with explicit constraints. Regression risk: **Behavioural**.

### AP-12: Missing Step Limit
**Signature:** No `recursion_limit`, max_steps, or similar bound on the agent's execution loop.
**Evidence:** LangGraph config or agent metadata has no step limit. Prompt has no "if you have tried X times..." rule.
**Risk:** Infinite loops on ambiguous inputs. Runaway cost.
**Fix type:** Add explicit step limit at runtime level and a "give up" rule in the prompt. Regression risk: **Safe**.

---

## Structure / architecture anti-patterns

### AP-13: Orphan Sub-Agent
**Signature:** `sub_agents` list declares agents that are never actually invoked under any described condition.
**Evidence:** Agent A declares `sub_agents: [agent_b]` but the prompt never describes when or how to call agent_b.
**Risk:** Dead declaration misleads reviewers. Model may invoke the sub-agent in unexpected situations.
**Fix type:** Either document the routing condition or remove from `sub_agents`. Regression risk: **Safe**.

### AP-14: Hidden Dependency
**Signature:** Agent calls a sub-agent or uses a tool that is not declared in its frontmatter.
**Evidence:** Prompt body references a tool name or agent name that does not appear in `tools.toolkits` or `sub_agents`.
**Risk:** Silent breakage when the undeclared dependency changes. Impossible to audit the dependency graph.
**Fix type:** Declare all dependencies in frontmatter. Regression risk: **Safe**.

### AP-15: Implicit Routing Contract
**Signature:** Supervisor delegates to sub-agents but the handoff payload is a free-form string, not a typed structure.
**Evidence:** `run_sub_agent("coder1c", task_description)` where `task_description` is an untyped narrative.
**Risk:** Sub-agent misinterprets the task. No way to validate the handoff before execution.
**Fix type:** Define a typed routing payload schema per destination agent. Regression risk: **Breaking**.

---

## Evaluation / observability anti-patterns

### AP-16: Untestable Agent
**Signature:** No dataset, no test file, no evaluation scenarios exist for this agent. Quality cannot be demonstrated.
**Evidence:** No files in `tests/` or `evals/` reference this agent. No documented positive/negative scenario set.
**Risk:** Any prompt change may break behavior. There is no way to know.
**Fix type:** Create minimal eval dataset: 5 positive, 3 negative, 2 edge cases. Regression risk: **Safe**.

### AP-17: Trace Without Signal
**Signature:** Logging exists (TraceCallbackHandler, server logs) but no product-level signals are emitted: wrong agent chosen, empty result returned, tool retry count.
**Evidence:** Generic request/response logs present but no counters or metrics for business-meaningful events.
**Risk:** Cannot localize failures in production. Cannot prove quality to stakeholders.
**Fix type:** Add 3-5 product metrics as structured log fields. Regression risk: **Safe**.
