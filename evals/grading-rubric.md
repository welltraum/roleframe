# Grading rubric

Use this rubric after a with-skill or without-skill run has finished and all produced files are available under `outputs/`.

## Assertion grading

- Mark `PASS` only with concrete evidence from the output.
- Mark `FAIL` when the artifact is absent, incomplete, or too vague to satisfy the assertion.
- Prefer file references, quoted headings, JSON keys, and visible file names as evidence.
- If the run crashes or produces no usable output, grade all unmet assertions as `FAIL`.

## Human review axes

Use blind comparison when both with-skill and without-skill outputs pass most mechanical checks.

Score each axis from `1` to `5`:

- `Structure`: Is the output easy to navigate and internally coherent?
- `Completeness`: Does it cover the core task without obvious holes?
- `Actionability`: Can another engineer use the result immediately?
- `Method fidelity`: Does it actually apply RoleFrame and IDEF0 instead of generic advice?
- `Evidence quality`: Are claims tied to concrete artifacts when review mode is used?

## Benchmarks

The benchmark should summarize:

- pass rate by configuration
- mean time and token usage
- comparison delta versus baseline
- notable qualitative wins or regressions

## Release gate

Do not cut a release when any of these conditions is true:

- a trigger-positive case fails to activate correctly
- a trigger-negative case auto-activates the skill
- a functional case fails on a required artifact
- benchmark output is missing for the current iteration
- install instructions cannot be reproduced from a clean machine
