#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = ROOT / "evals" / "evals.json"
WORKSPACE_ROOT = ROOT / "eval-workspace"


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
    return parser.parse_args()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def load_evals() -> list[dict]:
    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    return data["evals"]


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    iteration_dir = WORKSPACE_ROOT / f"iteration-{args.iteration}"
    iteration_dir.mkdir(parents=True, exist_ok=True)

    evals = load_evals()
    for item in evals:
        eval_dir = iteration_dir / f"eval-{slugify(item['id'])}"
        eval_dir.mkdir(parents=True, exist_ok=True)

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
                "skill_path": config["skill_path"],
                "input_files": item["files"],
                "output_dir": str(outputs_dir),
            }
            write_json(config_dir / "run-manifest.json", manifest)

    benchmark = {
        "iteration": args.iteration,
        "baseline_label": args.baseline_label,
        "eval_count": len(evals),
        "run_summary": {},
    }
    write_json(iteration_dir / "benchmark.json", benchmark)

    print(f"Prepared {len(evals)} eval directories in {iteration_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
