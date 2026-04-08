#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS_PATH = ROOT / "evals" / "evals.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render human-readable eval docs from evals/evals.json.")
    parser.add_argument("--check", action="store_true", help="Fail if generated docs are out of date.")
    return parser.parse_args()


def load_evals() -> list[dict]:
    payload = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    return payload["evals"]


def render_trigger_tests(evals: list[dict]) -> str:
    positive = [item for item in evals if "trigger" in item["tags"] and "negative" not in item["tags"]]
    negative = [item for item in evals if "trigger" in item["tags"] and "negative" in item["tags"]]

    lines = [
        "<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->",
        "# Trigger Tests",
        "",
        "Verify that `/roleframe` activates on relevant queries and does NOT activate on unrelated ones.",
        "",
        "## Should trigger",
        "",
        "| # | Query | Expected mode |",
        "|---|---|---|",
    ]
    for index, item in enumerate(positive, start=1):
        mode = next((tag for tag in item["tags"] if tag in {"design", "review", "help"}), "n/a")
        lines.append(f"| {index} | `{item['prompt']}` | {mode} |")

    lines.extend(
        [
            "",
            "## Should NOT trigger",
            "",
            "| # | Query | Why not |",
            "|---|---|---|",
        ]
    )
    for index, item in enumerate(negative, start=1):
        lines.append(f"| {index} | `{item['prompt']}` | {item['expected_output']} |")

    lines.extend(
        [
            "",
            "## How to test",
            "",
            "1. Start a fresh Codex session in this project.",
            "2. Run each query from `Should trigger` and verify the mode selection.",
            "3. Run each query from `Should NOT trigger` and verify the skill does not hijack the task.",
            "4. Save the raw response into the matching `outputs/response.md` file before grading.",
            "",
            "## Results log",
            "",
            "| # | Query | Expected | Actual | Pass? |",
            "|---|---|---|---|---|",
            "| | | | | |",
            "",
        ]
    )
    return "\n".join(lines)


def render_functional_tests(evals: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {"design": [], "review": []}
    for item in evals:
        if "functional" not in item["tags"]:
            continue
        for mode in grouped:
            if mode in item["tags"]:
                grouped[mode].append(item)
                break

    mode_titles = {
        "design": "Mode: design",
        "review": "Mode: review",
    }

    lines = [
        "<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->",
        "# Functional Tests",
        "",
        "Verify that each mode produces correct, complete output.",
        "",
        "Design outputs must follow the structured design package and generate markdown plus dashboard artifacts.",
        "Review outputs must follow the canonical audit package defined in `references/audit-template.md`.",
        "",
    ]
    for mode in ["design", "review"]:
        lines.extend([f"## {mode_titles[mode]}", ""])
        for item in grouped[mode]:
            label = item["id"].split("-")[-1].upper()
            lines.extend(
                [
                    f"### Test {label}: {item['expected_output']}",
                    "",
                    f"**Input:** `{item['prompt']}`",
                    "",
                    "**Expected behavior:**",
                ]
            )
            for assertion in item["assertions"]:
                lines.append(f"- [ ] {assertion}")
            lines.append("")

    lines.extend(
        [
            "## Eval workflow checks",
            "",
            "- Before grading `design`, verify the raw response, design markdown files, summary, and `dashboard.html`.",
            "- Before grading `review`, verify the raw response, audit markdown files, summary, and `dashboard.html`.",
            "- Run the first wave before the second wave in the risk-based cycle.",
            "",
        ]
    )
    return "\n".join(lines)


def render_comparison_tests(evals: list[dict]) -> str:
    comparisons = [item for item in evals if "comparison" in item["tags"]]

    lines = [
        "<!-- Generated from evals/evals.json by scripts/render_eval_docs.py. Do not edit manually. -->",
        "# Performance Comparison: With vs Without Skill",
        "",
        "Use these cases for a structured with-skill vs without-skill comparison.",
        "",
        "## Cases",
        "",
    ]
    for item in comparisons:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"**Prompt:** `{item['prompt']}`",
                "",
                f"**Expected improvement:** {item['expected_output']}",
                "",
                "**Assertions:**",
            ]
        )
        for assertion in item["assertions"]:
            lines.append(f"- [ ] {assertion}")
        lines.append("")

    lines.extend(
        [
            "## Results log",
            "",
            "| Test | Without skill (notes) | With skill (notes) | Improvement? |",
            "|---|---|---|---|",
            "| | | | |",
            "",
        ]
    )
    return "\n".join(lines)


def write_or_check(path: Path, content: str, check: bool) -> bool:
    expected = content.rstrip() + "\n"
    if check:
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current != expected:
            print(f"OUTDATED: {path.relative_to(ROOT)}", file=sys.stderr)
            return False
        return True

    path.write_text(expected, encoding="utf-8")
    return True


def main() -> int:
    args = parse_args()
    evals = load_evals()
    ok = True
    ok &= write_or_check(ROOT / "evals" / "trigger-tests.md", render_trigger_tests(evals), args.check)
    ok &= write_or_check(ROOT / "evals" / "functional-tests.md", render_functional_tests(evals), args.check)
    ok &= write_or_check(ROOT / "evals" / "performance-comparison.md", render_comparison_tests(evals), args.check)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
