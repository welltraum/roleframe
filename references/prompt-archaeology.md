# Prompt archaeology

## Quick map

- Role reconstruction
- SOP reconstruction
- Constraints
- Output contract
- Mechanism map
- Function test
- Context budget check
- Final reconstruction sentence

Use this guide when auditing agents that were **not built with IDEF0 in mind** — agents where there is no formal structure, only a monolithic prompt and a frontmatter with toolkits.

The goal: reconstruct the implicit IDEF0 from the prompt text, then use the gap between "what the prompt implies" and "what IDEF0 requires" as the audit finding.

---

## Step 1: Find the implicit role (Control → role)

**Where to look:** First 3-10 lines of the prompt body.

**Patterns:**
- `You are [X]` — explicit role. Note whether X is narrow ("a routing agent for 1C queries") or vague ("a helpful assistant").
- `Your goal is to [X]` — goal statement. Often mixed with scope.
- Absence of any role declaration — the agent has no identity. Score Control layer at most 1.

**What to extract:**
- The claimed role
- Whether the claimed role matches the actual instructions below (Role Identity Drift, AP-5)
- What the implicit scope is even if not stated

---

## Step 2: Reconstruct the implicit SOP (Control → SOP)

**Where to look:** Numbered lists, "first/then/finally" sequences, conditional blocks ("if X, do Y").

**Reconstruction technique:**
1. Find all imperative sentences in the prompt ("Query the database", "Ask the user for clarification", "Return the result as...").
2. Group them by topic — these become candidate SOP steps.
3. Look for ordering signals: "always start with", "before calling", "only after", "as a last resort".
4. Check if the sequence is complete: does it cover how the agent starts, what it does in the middle, and how it terminates?

**Signs of implicit vs explicit SOP:**
- Explicit: numbered or lettered steps with conditions and exit criteria
- Implicit: scattered instructions, examples used as proxies for rules, no clear terminal state
- Missing: no sequencing at all — model improvises order

**What to note:**
- Is there a step for handling empty results? For tool errors?
- Is there a maximum number of retries or a give-up condition?
- Does the SOP cover all inputs claimed in the frontmatter tools?

---

## Step 3: Extract implicit constraints (Control → constraints)

**Where to look:** Negative instructions, "do not" / "never" / "only" / "always" statements, examples with incorrect behavior crossed out.

**Patterns to find:**
- `Do not [X]` — explicit prohibition
- `Only use [tool] when [condition]` — scoped permission
- `If the user asks about [X], explain that you cannot help` — boundary enforcement
- Absence of any constraints → score Safety criterion at 0-1

**What to extract:**
- List of explicit prohibitions
- List of scoped permissions
- What is NOT constrained (the implicit free-fire zone) — this is often where problems occur

---

## Step 4: Infer the output contract (Control → output contract)

**Where to look:** Last sections of the prompt, "return", "respond with", "output", "format your answer as" phrases, and any examples.

**Reconstruction technique:**
1. Find all mentions of what the agent should return.
2. Check if a format is specified (JSON, markdown, plain text) or assumed.
3. Look for examples — they are the de facto contract even if no schema exists.
4. Check whether examples cover only success or also empty/error cases.

**What to note:**
- Is the output format machine-readable or human-readable?
- Does the consumer (supervisor or user) need to parse this output? If yes, AP-6/AP-7/AP-8 likely apply.
- What happens on empty result — is it defined anywhere?

---

## Step 5: Map the mechanism (Mechanism layer)

**Where to look:** `tools.toolkits` in frontmatter, tool names referenced in prompt body, middleware list.

**Reconstruction technique:**
1. List every tool name that appears in either frontmatter or prompt body.
2. For each tool: what does the prompt say to do with its output? What does it say to do when it fails?
3. Check for tools in frontmatter that the prompt never mentions — candidates for AP-13 (Orphan Sub-Agent) or AP-14 (Hidden Dependency).
4. Check for tool names in the prompt that are not in frontmatter — undeclared dependencies.

**Context window estimate:**
Count prompt lines and estimate token count: ~1 token per 4 characters for English, ~1 token per 2-3 characters for Russian/code. Flag if the static prompt is likely > 2000 tokens — it leaves less room for dynamic context and history.

A rough formula: `char_count / 3.5 ≈ token_estimate`. If token_estimate > 2000, add to backlog as a context budget issue.

---

## Step 6: Reconstruct the actual business function

After steps 1-5, write one sentence:

> "[Agent name] takes [reconstructed inputs] and [reconstructed SOP summary] to produce [reconstructed output], governed by [reconstructed constraints]."

Compare this to the claimed role from step 1. Gaps between the claimed and reconstructed function are the most important findings.

**The "one sentence" test:** If you cannot write this sentence — the function is not atomic. That is the primary audit finding, and it takes precedence over all criteria scoring.

---

## Step 7: Cross-reference against anti-patterns

After reconstruction, scan [anti-patterns.md](anti-patterns.md) systematically. With the implicit IDEF0 reconstructed, most patterns become detectable:

- AP-1 (God Prompt): does the prompt cover more than one of the four IDEF0 quadrants per section?
- AP-2 (Implicit State Machine): did you find ordering in step 2 that relies on examples rather than explicit states?
- AP-5 (Role Identity Drift): does the reconstructed function from step 6 match the declared role from step 1?
- AP-6/7/8 (Output contract issues): what did step 4 produce?
- AP-9/10 (Tool issues): what did step 5 produce?

---

## Output of archaeology

After running all 7 steps, you have:

1. **Reconstructed IDEF0 card** — fill it in even if implicit
2. **Gap list** — what IDEF0 requires vs what was found
3. **Anti-pattern hits** — which of AP-1 through AP-17 fire
4. **One-sentence function test result** — atomic or needs decomposition
5. **Context window estimate** — token count of static prompt

Feed all of this into the standard 12-section audit template.
