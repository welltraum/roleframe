#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "PyYAML>=6.0.2",
# ]
# ///

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"
EVALS_PATH = ROOT / "evals" / "evals.json"
RENDER_EVAL_DOCS_PATH = ROOT / "scripts" / "render_eval_docs.py"

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the roleframe skill package.")
    parser.add_argument(
        "--skip-skills-ref",
        action="store_true",
        help="Skip the official skills-ref validator and run only repository checks.",
    )
    return parser.parse_args()


def read_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path.name} must start with YAML frontmatter")

    parts = text.split("---\n", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name} has an unterminated YAML frontmatter block")

    data = yaml.safe_load(parts[1]) or {}
    body = parts[2]
    return data, body


def iter_markdown_files() -> list[Path]:
    files = [SKILL_PATH]
    files.extend(sorted((ROOT / "references").glob("*.md")))
    return files


def collect_relative_paths(text: str) -> set[str]:
    candidates: set[str] = set()
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target or "://" in target or target.startswith("#"):
            continue
        candidates.add(target)
    return candidates


def validate_links(errors: list[str]) -> None:
    for path in iter_markdown_files():
        text = path.read_text(encoding="utf-8")
        for target in sorted(collect_relative_paths(text)):
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"Broken relative reference in {path.relative_to(ROOT)}: {target}")


def validate_frontmatter(frontmatter: dict, errors: list[str], warnings: list[str]) -> None:
    required = ["name", "description", "license"]
    for key in required:
        if key not in frontmatter or not frontmatter[key]:
            errors.append(f"Missing required frontmatter field: {key}")

    if frontmatter.get("name") != ROOT.name:
        errors.append(
            f"Frontmatter name `{frontmatter.get('name')}` does not match directory name `{ROOT.name}`"
        )

    line_count = sum(1 for _ in SKILL_PATH.open("r", encoding="utf-8"))
    if line_count > 500:
        errors.append(f"SKILL.md exceeds the 500-line guideline: {line_count} lines")

    char_count = len(SKILL_PATH.read_text(encoding="utf-8"))
    approx_tokens = round(char_count / 4)
    if approx_tokens > 5000:
        errors.append(f"SKILL.md exceeds the 5000-token guideline: ~{approx_tokens} tokens")
    elif approx_tokens > 4500:
        warnings.append(f"SKILL.md is close to the 5000-token guideline: ~{approx_tokens} tokens")


def validate_evals(frontmatter: dict, errors: list[str]) -> None:
    if not EVALS_PATH.exists():
        errors.append("Missing evals/evals.json")
        return

    data = json.loads(EVALS_PATH.read_text(encoding="utf-8"))
    if data.get("skill_name") != frontmatter.get("name"):
        errors.append(
            f"evals/evals.json skill_name `{data.get('skill_name')}` does not match `{frontmatter.get('name')}`"
        )

    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        errors.append("evals/evals.json must contain a non-empty `evals` list")
        return

    required_keys = {"id", "prompt", "expected_output", "files", "assertions", "tags"}
    ids: set[str] = set()
    for item in evals:
        missing = required_keys - set(item)
        if missing:
            errors.append(f"Eval case is missing keys {sorted(missing)}: {item.get('id', '<unknown>')}")
            continue

        if item["id"] in ids:
            errors.append(f"Duplicate eval id: {item['id']}")
        ids.add(item["id"])

        if not isinstance(item["assertions"], list) or not item["assertions"]:
            errors.append(f"Eval `{item['id']}` must have a non-empty assertions list")

        if not isinstance(item["files"], list):
            errors.append(f"Eval `{item['id']}` must have a files list")
            continue

        for file_ref in item["files"]:
            ref_path = ROOT / file_ref
            if not ref_path.exists():
                errors.append(f"Eval `{item['id']}` references missing file: {file_ref}")


def run_skills_ref() -> tuple[bool, str]:
    command: list[str]
    if shutil.which("skills-ref"):
        command = ["skills-ref", "validate", str(ROOT)]
    elif shutil.which("uvx"):
        command = [
            "uvx",
            "--from",
            "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref",
            "skills-ref",
            "validate",
            str(ROOT),
        ]
    else:
        return False, "skills-ref not found and uvx is unavailable"

    env = os.environ.copy()
    cache_root = ROOT / ".cache" / "uv"
    data_root = ROOT / ".cache" / "uv-data"
    bin_root = ROOT / ".cache" / "uv-bin"
    cache_root.mkdir(parents=True, exist_ok=True)
    data_root.mkdir(parents=True, exist_ok=True)
    bin_root.mkdir(parents=True, exist_ok=True)
    env.setdefault("UV_CACHE_DIR", str(cache_root))
    env.setdefault("XDG_DATA_HOME", str(data_root))
    env.setdefault("XDG_BIN_HOME", str(bin_root))

    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part).strip()
    return completed.returncode == 0, output


def check_generated_eval_docs() -> tuple[bool, str]:
    completed = subprocess.run(
        [sys.executable, str(RENDER_EVAL_DOCS_PATH), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part).strip()
    return completed.returncode == 0, output


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        frontmatter, _ = read_frontmatter(SKILL_PATH)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    validate_frontmatter(frontmatter, errors, warnings)
    validate_links(errors)
    validate_evals(frontmatter, errors)

    ok, output = check_generated_eval_docs()
    if not ok:
        errors.append("Generated eval docs are out of date; run scripts/render_eval_docs.py")
    if output:
        print(output)

    if not args.skip_skills_ref:
        ok, output = run_skills_ref()
        if not ok:
            errors.append("skills-ref validation failed")
        if output:
            print(output)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
