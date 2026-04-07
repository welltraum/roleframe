#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate grading and timing outputs for one eval iteration.")
    parser.add_argument("--iteration-dir", required=True, help="Path to an iteration directory in eval-workspace.")
    parser.add_argument(
        "--baseline-label",
        default="without_skill",
        help="Baseline configuration label. Default: without_skill",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "stddev": 0.0}
    if len(values) == 1:
        return {"mean": values[0], "stddev": 0.0}
    return {"mean": statistics.mean(values), "stddev": statistics.pstdev(values)}


def main() -> int:
    args = parse_args()
    iteration_dir = Path(args.iteration_dir).resolve()
    eval_dirs = sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-"))

    per_config: dict[str, dict[str, list[float]]] = {}
    per_eval: dict[str, dict] = {}

    for eval_dir in eval_dirs:
        per_eval[eval_dir.name] = {}
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            grading = read_json(config_dir / "grading.json")
            timing = read_json(config_dir / "timing.json")
            if grading is None or timing is None:
                continue

            pass_rate = float(grading.get("summary", {}).get("pass_rate", 0.0))
            total_tokens = float(timing.get("total_tokens", 0))
            duration_ms = float(timing.get("duration_ms", 0))

            bucket = per_config.setdefault(
                config_dir.name,
                {"pass_rate": [], "tokens": [], "time_seconds": []},
            )
            bucket["pass_rate"].append(pass_rate)
            bucket["tokens"].append(total_tokens)
            bucket["time_seconds"].append(duration_ms / 1000.0)

            per_eval[eval_dir.name][config_dir.name] = {
                "pass_rate": pass_rate,
                "tokens": total_tokens,
                "time_seconds": duration_ms / 1000.0,
            }

    run_summary: dict[str, dict] = {}
    for config_name, metrics in per_config.items():
        run_summary[config_name] = {
            "pass_rate": summarize(metrics["pass_rate"]),
            "time_seconds": summarize(metrics["time_seconds"]),
            "tokens": summarize(metrics["tokens"]),
        }

    baseline = run_summary.get(args.baseline_label, {})
    with_skill = run_summary.get("with_skill", {})
    delta = {
        "pass_rate": round(
            with_skill.get("pass_rate", {}).get("mean", 0.0) - baseline.get("pass_rate", {}).get("mean", 0.0),
            4,
        ),
        "time_seconds": round(
            with_skill.get("time_seconds", {}).get("mean", 0.0)
            - baseline.get("time_seconds", {}).get("mean", 0.0),
            4,
        ),
        "tokens": round(
            with_skill.get("tokens", {}).get("mean", 0.0) - baseline.get("tokens", {}).get("mean", 0.0),
            4,
        ),
    }
    run_summary["delta"] = delta

    payload = {
        "iteration_dir": str(iteration_dir),
        "baseline_label": args.baseline_label,
        "run_summary": run_summary,
        "per_eval": per_eval,
    }
    (iteration_dir / "benchmark.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote benchmark summary to {iteration_dir / 'benchmark.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
