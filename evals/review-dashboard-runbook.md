# Review and package eval runbook

This runbook defines the canonical manual-first loop for the RoleFrame review testbed and the structured package renderers.

All `uv` commands in this repository should use workspace-local caches:

```bash
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin uv run ...
```

Without those overrides, sandboxed environments may fail for reasons unrelated to the Skill itself.

## Dependencies

- `uv`
- Python 3.12+
- [`scripts/validate_skill.py`](../scripts/validate_skill.py)
- [`scripts/prepare_eval.py`](../scripts/prepare_eval.py)
- [`scripts/check_eval_artifacts.py`](../scripts/check_eval_artifacts.py)
- [`scripts/benchmark_eval.py`](../scripts/benchmark_eval.py)

## Model matrix

For the first Codex-only cycle, start with wave 1 and one target model. Expand to a fast-model plus reasoning-model matrix only after wave 1 is healthy.

For broader release validation, run the same iteration on at least two models:

- Fast model: use the cheapest model you expect users to run regularly.
- Reasoning model: use the main higher-quality model you expect to rely on for reviews.

The purpose is simple: catch Skills that are too underspecified for smaller models or too verbose for stronger models.

## Canonical fixtures

- Review testbed: [`evals/files/sample-agents`](./files/sample-agents)
- Review dashboard smoke fixture: [`evals/files/sample-audits`](./files/sample-audits)
- Design package smoke fixture: [`evals/files/sample-design-package`](./files/sample-design-package)
- Expected findings baseline: [`evals/expected-findings.md`](./expected-findings.md)

## Output convention

Store generated artifacts under each run's `outputs/` directory.

- Raw model response: `outputs/response.md`
- Structured audit package: `outputs/docs/agent_audit/*.audit.json`
- Rendered audit views: `outputs/docs/agent_audit/*.md`
- Audit summary: `outputs/docs/agent_audit/README.md`
- Structured summary: `outputs/docs/agent_audit/summary.audit.json`
- Dashboard HTML: `outputs/docs/agent_audit/dashboard.html`

If the client exports a raw response with a different extension, normalize it to `response.md` before grading.

## Workflow

1. Validate the repository shape and generated eval docs.

   ```bash
   UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
     uv run scripts/validate_skill.py --skip-skills-ref
   ```

2. Prepare a fresh iteration workspace.

   ```bash
   UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
     uv run scripts/prepare_eval.py --iteration 2026-04-07 --wave 1
   ```

   The iteration directory will include:

   - pending `grading.json` and `timing.json` templates for every run
   - `scenario-matrix.csv` for the first-cycle verdict table
   - `defect-log.md` and `ambiguous-cases.md` for expert decisions

3. Run the prepared prompts manually for each config in the target model matrix.

4. Save the raw response and generated artifacts into the matching `outputs/` directory.

5. Verify artifact completeness before grading.

   ```bash
   UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
     uv run scripts/check_eval_artifacts.py --iteration-dir eval-workspace/iteration-2026-04-07
   ```

   This check now validates both file presence and minimal content signals. In particular:

   - review outputs must include structured audit JSON plus rendered markdown views
   - review outputs must include evidence references in the audit package
   - review dashboard HTML must contain dense agent blocks for evidence, criteria, contracts, backlog, and patch plan
   - design dashboard HTML must contain dense agent blocks for business function, control, mechanism, contracts, evaluation, and delivery
   - `functional-review-r1` is checked against the expected findings baseline heuristically

6. Fill `grading.json` and `timing.json` for each completed run.

   Use these minimum fields:

   - `grading.json`: assertion statuses, evidence, `summary.pass_rate`, `expert_verdict`, `expert_notes`
   - `timing.json`: model, date, duration, input/output/total tokens

7. Aggregate the iteration.

   ```bash
   UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin \
     uv run scripts/benchmark_eval.py --iteration-dir eval-workspace/iteration-2026-04-07
   ```

   Aggregation writes:

   - `benchmark.json`
   - `release-gate.json`
   - `scenario-matrix.csv`
   - `scenario-matrix.md`

## Feedback loop

Use the same fix loop for `review` and `design`:

1. Run the prompt.
2. Check that the required artifacts exist.
3. Grade the result against assertions and expected findings.
4. Fix the smallest reliable source of failure:
   - fixture defect if the scenario is not stable,
   - eval wording if the assertion is ambiguous,
   - skill wording if the instruction is missing or conflicting.
5. Re-run the same scenario.

Do not patch `SKILL.md` first when the real problem is a broken fixture or unclear eval case.
