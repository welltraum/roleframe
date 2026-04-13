# Prompt archaeology

Use this guide only when the review profile is `agent` and the system was not designed explicitly with IDEF0.

For `pack`, use artifact archaeology across manifest, routes, tests, and proof surfaces. For `workflow`, start with decomposition.

## Quick map

- Role reconstruction
- SOP reconstruction
- Constraints
- Output contract
- Mechanism map
- Boundary sentence
- Context budget check

## Step 1: Reconstruct the role

Look at the first lines of the prompt:

- `You are [X]`
- `Your job is to [X]`
- missing role declaration

Extract the claimed role and check whether it matches the rest of the file.

## Step 2: Reconstruct the SOP

Find:

- imperative steps
- ordering signals
- branch conditions
- stop conditions

If the sequence exists only in examples, treat that as AP-2.

## Step 3: Extract constraints

Collect:

- `do not`
- `never`
- `only`
- scoped tool permissions

Also record what remains unconstrained.

## Step 4: Infer the contract

Find all lines that describe output. Check:

- is the format machine-readable?
- does it include empty and failure paths?
- is the consumer expected to parse it?

## Step 5: Cross-check mechanism

Compare:

- prompt tool mentions
- frontmatter toolkits
- runtime or tool factory

If they disagree, trust runtime and record the mismatch.

## Step 6: Write the boundary sentence

Write one sentence:

> `[unit] takes [input] and follows [core SOP] to produce [output] under [constraints].`

If you cannot write that sentence, the unit is too broad or incoherent.

## Step 7: Estimate static context cost

Approximate token load with `char_count / 3.5`.

If the static prompt is likely over 2000 tokens, add a context-budget finding.

## Output of archaeology

After these steps, you should have:

1. reconstructed IDEF0
2. gap list between implied and required contract
3. anti-pattern hits
4. boundary sentence
5. context-budget finding if needed
