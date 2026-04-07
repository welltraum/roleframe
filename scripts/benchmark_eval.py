#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import csv
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


def is_completed(record: dict | None) -> bool:
    if not record:
        return False
    return record.get("status", "completed") == "completed"


def artifact_lookup(iteration_dir: Path) -> dict[tuple[str, str], dict]:
    payload = read_json(iteration_dir / "artifact-check.json") or {}
    lookup: dict[tuple[str, str], dict] = {}
    for eval_name, eval_report in payload.get("results", {}).items():
        for config_name, config_report in eval_report.items():
            lookup[(eval_name, config_name)] = config_report
    return lookup


def pass_fail_status(grading: dict | None) -> str:
    if not grading or grading.get("status") == "pending":
        return "pending"
    if grading.get("summary", {}).get("pass"):
        return "pass"
    return "fail"


def verdict_status(grading: dict | None) -> str:
    if not grading:
        return "pending"
    return grading.get("expert_verdict", {}).get("overall", "pending")


def artifacts_status(report: dict | None) -> str:
    if not report:
        return "pending"
    return "pass" if report.get("ok") else "fail"


def blocker_status(blocking: bool, pass_fail: str, artifacts_ok: str, verdict: str) -> str:
    if not blocking:
        return "no"
    if "pending" in {pass_fail, artifacts_ok, verdict}:
        return "pending"
    if pass_fail == "fail" or artifacts_ok == "fail" or verdict == "rework required":
        return "yes"
    return "no"


def write_matrix(iteration_dir: Path, rows: list[dict]) -> None:
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

    lines = [
        "# Scenario matrix",
        "",
        "| Scenario | Config | Wave | Blocking | Pass/fail | Artifacts ok? | Expert verdict | Blocker? |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['config']} | {row['wave']} | {row['blocking']} | "
            f"{row['pass_fail']} | {row['artifacts_ok']} | {row['expert_verdict']} | {row['blocker']} |"
        )
    (iteration_dir / "scenario-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    iteration_dir = Path(args.iteration_dir).resolve()
    eval_dirs = sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-"))

    per_config: dict[str, dict[str, list[float]]] = {}
    per_eval: dict[str, dict] = {}
    rows: list[dict] = []
    artifacts = artifact_lookup(iteration_dir)
    release_gate: list[dict] = []

    for eval_dir in eval_dirs:
        per_eval[eval_dir.name] = {}
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            manifest = read_json(config_dir / "run-manifest.json")
            grading = read_json(config_dir / "grading.json")
            timing = read_json(config_dir / "timing.json")
            if manifest is None:
                continue

            report = artifacts.get((eval_dir.name, config_dir.name))
            pass_fail = pass_fail_status(grading)
            artifacts_ok = artifacts_status(report)
            verdict = verdict_status(grading)
            blocking = bool(manifest.get("blocking", False))
            blocker = blocker_status(blocking, pass_fail, artifacts_ok, verdict)

            rows.append(
                {
                    "scenario": manifest["id"],
                    "config": config_dir.name,
                    "wave": manifest.get("wave", ""),
                    "blocking": "yes" if blocking else "no",
                    "pass_fail": pass_fail,
                    "artifacts_ok": artifacts_ok,
                    "expert_verdict": verdict,
                    "blocker": blocker,
                }
            )

            per_eval[eval_dir.name][config_dir.name] = {
                "pass_fail": pass_fail,
                "artifacts_ok": artifacts_ok,
                "expert_verdict": verdict,
                "blocking": blocking,
                "blocker": blocker,
            }

            if blocking and config_dir.name == "with_skill":
                release_gate.append(
                    {
                        "eval_id": manifest["id"],
                        "pass_fail": pass_fail,
                        "artifacts_ok": artifacts_ok,
                        "expert_verdict": verdict,
                        "blocker": blocker,
                    }
                )

            if not (is_completed(grading) and is_completed(timing)):
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

            per_eval[eval_dir.name][config_dir.name].update(
                {
                    "pass_rate": pass_rate,
                    "tokens": total_tokens,
                    "time_seconds": duration_ms / 1000.0,
                }
            )

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

    gate_ready = bool(release_gate) and all(item["blocker"] == "no" for item in release_gate)
    release_gate_payload = {
        "iteration_dir": str(iteration_dir),
        "ready": gate_ready,
        "blocking_cases": release_gate,
    }
    (iteration_dir / "release-gate.json").write_text(
        json.dumps(release_gate_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    write_matrix(iteration_dir, rows)

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
    print(f"Wrote release gate summary to {iteration_dir / 'release-gate.json'}")
    print(f"Wrote scenario matrix to {iteration_dir / 'scenario-matrix.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
