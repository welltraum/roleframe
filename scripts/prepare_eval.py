#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = ROOT / "evals" / "evals.json"
WORKSPACE_ROOT = ROOT / "eval-workspace"

FIRST_WAVE_IDS = {
    "functional-design-d1",
    "functional-design-d2",
    "functional-design-d3",
    "functional-design-d4",
    "functional-review-r1",
    "functional-review-r4",
    "comparison-a",
    "comparison-b",
    "comparison-c",
}

BLOCKING_IDS = {
    "functional-design-d1",
    "functional-design-d2",
    "functional-design-d4",
    "functional-review-r1",
    "functional-review-r4",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a fresh eval workspace iteration.")
    parser.add_argument("--iteration", required=True, help="Iteration label, for example `1` or `2026-04-07`.")
    parser.add_argument(
        "--baseline-label",
        default="without_skill",
        help="Baseline run label. Default: without_skill",
    )
    parser.add_argument(
        "--previous-skill-path",
        help="Optional path to a previous skill snapshot. Creates an `old_skill` run manifest.",
    )
    parser.add_argument(
        "--wave",
        choices=["all", "1", "2"],
        default="all",
        help="Prepare only the first-cycle risk-based wave, the second wave, or all evals. Default: all",
    )
    return parser.parse_args()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_evals() -> list[dict]:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    return data["evals"]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json_if_missing(path: Path, payload: dict) -> None:
    if path.exists():
        return
    write_json(path, payload)


def eval_wave(eval_id: str, tags: list[str]) -> int:
    if "trigger" in tags or eval_id in FIRST_WAVE_IDS:
        return 1
    return 2


def is_blocking(eval_id: str, tags: list[str]) -> bool:
    if "trigger" in tags:
        return True
    return eval_id in BLOCKING_IDS


def include_eval(eval_id: str, tags: list[str], selected_wave: str) -> bool:
    if selected_wave == "all":
        return True
    return eval_wave(eval_id, tags) == int(selected_wave)


def artifact_expectations(eval_id: str, tags: list[str], config_name: str) -> dict:
    required_with_skill = ["raw_response"]
    forbidden_with_skill: list[str] = []

    if config_name != "with_skill":
        return {
            "required": ["raw_response"],
            "forbidden": [],
        }

    if "trigger" in tags or "comparison" in tags:
        return {
            "required": required_with_skill,
            "forbidden": forbidden_with_skill,
        }

    if "review" in tags:
        required_with_skill.extend(["audit_summary", "dashboard_html", "agent_audits", "structured_audits", "structured_summary"])
    elif "design" in tags:
        required_with_skill.extend(["design_summary", "dashboard_html", "agent_designs", "structured_designs", "structured_design_summary"])

    return {
        "required": required_with_skill,
        "forbidden": forbidden_with_skill,
    }


def grading_template(manifest: dict, config_name: str) -> dict:
    return {
        "status": "pending",
        "eval_id": manifest["id"],
        "config": config_name,
        "summary": {
            "passed": 0,
            "total": len(manifest["assertions"]),
            "pass_rate": 0.0,
            "pass": False,
        },
        "assertions": [
            {
                "id": index + 1,
                "text": assertion,
                "status": "PENDING",
                "evidence": "",
            }
            for index, assertion in enumerate(manifest["assertions"])
        ],
        "expert_verdict": {
            "method_fidelity": "pending",
            "engineering_usefulness": "pending",
            "evidence_quality": "pending",
            "artifact_readiness": "pending",
            "overall": "pending",
        },
        "expert_notes": "",
        "blocker": bool(manifest["blocking"]),
        "defect_log": [],
    }


def timing_template(manifest: dict, config_name: str) -> dict:
    return {
        "status": "pending",
        "eval_id": manifest["id"],
        "config": config_name,
        "model": "",
        "run_at": "",
        "duration_ms": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }


def write_iteration_files(iteration_dir: Path, rows: list[dict]) -> None:
    readme = """# Eval iteration workspace

Use workspace-local caches for `uv` commands in this repository:

```bash
UV_CACHE_DIR=.cache/uv XDG_DATA_HOME=.cache/uv-data XDG_BIN_HOME=.cache/uv-bin uv run ...
```

Recommended first cycle:

1. Run `scripts/validate_skill.py --skip-skills-ref`
2. Run the prepared prompts for wave 1 first
3. Save `response.md` and generated artifacts under each `outputs/`
4. Replace the pending `grading.json` and `timing.json` values
5. Run `scripts/check_eval_artifacts.py`
6. Run `scripts/benchmark_eval.py`
"""
    readme_path = iteration_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(readme, encoding="utf-8")

    defect_log = """# Defect log

| Scenario | Config | Type | Severity | Summary | Notes |
|---|---|---|---|---|---|
"""
    defect_log_path = iteration_dir / "defect-log.md"
    if not defect_log_path.exists():
        defect_log_path.write_text(defect_log, encoding="utf-8")

    ambiguous = """# Ambiguous cases

| Scenario | Question | Why it is ambiguous | Expert decision | Notes |
|---|---|---|---|---|
"""
    ambiguous_path = iteration_dir / "ambiguous-cases.md"
    if not ambiguous_path.exists():
        ambiguous_path.write_text(ambiguous, encoding="utf-8")

    csv_path = iteration_dir / "scenario-matrix.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "config",
                "wave",
                "blocking",
                "pass_fail",
                "artifacts_ok",
                "expert_verdict",
                "blocker",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    args = parse_args()
    iteration_dir = WORKSPACE_ROOT / f"iteration-{args.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    evals = load_evals()
    scenario_rows: list[dict] = []
    prepared_count = 0
    prepared_evals = 0
    for item in evals:
        if not include_eval(item["id"], item["tags"], args.wave):
            continue

        eval_dir = iteration_dir / f"eval-{slugify(item['id'])}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        wave = eval_wave(item["id"], item["tags"])
        blocking = is_blocking(item["id"], item["tags"])
        prepared_evals += 1

        run_configs = {
            "with_skill": {
                "skill_path": str(ROOT),
                "prompt": item["prompt"],
            },
            args.baseline_label: {
                "skill_path": None,
                "prompt": item["prompt"],
            },
        }

        if args.previous_skill_path:
            run_configs["old_skill"] = {
                "skill_path": str(Path(args.previous_skill_path).resolve()),
                "prompt": item["prompt"],
            }

        for config_name, config in run_configs.items():
            config_dir = eval_dir / config_name
            outputs_dir = config_dir / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            manifest = {
                "id": item["id"],
                "prompt": config["prompt"],
                "expected_output": item["expected_output"],
                "assertions": item["assertions"],
                "tags": item["tags"],
                "wave": wave,
                "blocking": blocking,
                "skill_path": config["skill_path"],
                "input_files": item["files"],
                "output_dir": str(outputs_dir),
                "artifact_expectations": artifact_expectations(item["id"], item["tags"], config_name),
            }
            write_json(config_dir / "run-manifest.json", manifest)
            write_json_if_missing(config_dir / "grading.json", grading_template(manifest, config_name))
            write_json_if_missing(config_dir / "timing.json", timing_template(manifest, config_name))
            prepared_count += 1
            scenario_rows.append(
                {
                    "scenario": item["id"],
                    "config": config_name,
                    "wave": wave,
                    "blocking": "yes" if blocking else "no",
                    "pass_fail": "pending",
                    "artifacts_ok": "pending",
                    "expert_verdict": "pending",
                    "blocker": "pending" if blocking else "no",
                }
            )

    benchmark = {
        "iteration": args.iteration,
        "baseline_label": args.baseline_label,
        "eval_count": prepared_evals,
        "run_summary": {},
    }
    write_json(iteration_dir / "benchmark.json", benchmark)
    write_iteration_files(iteration_dir, scenario_rows)

    print(f"Prepared {prepared_count} run directories in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
