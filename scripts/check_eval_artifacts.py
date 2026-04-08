#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


EVIDENCE_RE = re.compile(r"(#L\d+(?:-L\d+)?)|(:\d+(?:-\d+)?)")

FINDING_PATTERNS = {
    "supervisor_scope_too_broad": [
        r"scope",
        r"boundary",
        r"маршрутизац",
        r"финальн",
        r"too broad",
        r"размыт",
    ],
    "routing_contract_is_implicit": [
        r"routing contract",
        r"handoff",
        r"implicit",
        r"typed payload",
        r"маршрут",
        r"контракт",
        r"типиз",
    ],
    "output_contract_is_missing": [
        r"output contract",
        r"free-form",
        r"schema",
        r"контракт ответа",
        r"схем",
        r"free text",
    ],
    "hidden_or_weak_tool_assumptions": [
        r"archive_search",
        r"hidden dependency",
        r"undeclared",
        r"tool policy",
        r"необъяв",
        r"скрыт",
    ],
    "tool_failure_strategy_is_weak": [
        r"tool fail",
        r"timeout",
        r"retry",
        r"сбой инструмента",
        r"таймаут",
        r"ошибк",
    ],
    "handoff_payload_is_untyped": [
        r"untyped",
        r"fixed structure",
        r"handoff payload",
        r"нет фиксирован",
        r"нет схем",
        r"payload",
    ],
    "unsafe_completion_behavior_exists": [
        r"fill the gaps",
        r"hallucinat",
        r"додумыва",
        r"complete response",
        r"smooth out the gaps",
    ],
    "eval_and_ops_gaps_remain": [
        r"observability",
        r"eval coverage",
        r"change management",
        r"partial eval",
        r"наблюдаем",
        r"покрыт.*eval",
        r"operations",
    ],
}

STRUCTURED_AGENT_REQUIRED = {
    "metadata",
    "summary",
    "idef0",
    "criteria",
    "evidence_points",
    "contracts",
    "anti_patterns",
    "backlog",
    "patch_plan",
}

STRUCTURED_SUMMARY_REQUIRED = {
    "language",
    "title",
    "subtitle",
    "overall_verdict",
    "overview_cards",
    "canonical_findings",
    "architecture",
    "critical_issues",
    "maturity_matrix",
    "contract_matrix",
    "roadmap",
    "agents_lead",
}

STRUCTURED_DESIGN_REQUIRED = {
    "metadata",
    "summary",
    "business_function",
    "idef0",
    "control_spec",
    "mechanism_spec",
    "contracts",
    "dependencies",
    "evaluation_plan",
    "delivery_plan",
}

STRUCTURED_DESIGN_SUMMARY_REQUIRED = {
    "language",
    "title",
    "subtitle",
    "overall_verdict",
    "overview_cards",
    "architecture",
    "critical_risks",
    "contract_matrix",
    "implementation_phases",
    "agents_lead",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate expected eval artifacts for one iteration.")
    parser.add_argument("--iteration-dir", required=True, help="Path to an iteration directory in eval-workspace.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def candidate_paths(artifact_id: str, output_dir: Path) -> list[Path]:
    mapping = {
        "raw_response": [
            output_dir / "response.md",
            output_dir / "response.txt",
            output_dir / "response.json",
        ],
        "audit_summary": [output_dir / "docs" / "agent_audit" / "README.md"],
        "structured_summary": [output_dir / "docs" / "agent_audit" / "summary.audit.json"],
        "dashboard_html": [
            output_dir / "docs" / "agent_audit" / "dashboard.html",
            output_dir / "docs" / "agent_design" / "dashboard.html",
        ],
        "agent_audits": list((output_dir / "docs" / "agent_audit").glob("[0-9][0-9]_*.md")),
        "structured_audits": list((output_dir / "docs" / "agent_audit").glob("[0-9][0-9]_*.audit.json")),
        "design_summary": [output_dir / "docs" / "agent_design" / "README.md"],
        "structured_design_summary": [output_dir / "docs" / "agent_design" / "summary.design.json"],
        "agent_designs": list((output_dir / "docs" / "agent_design").glob("[0-9][0-9]_*.md")),
        "structured_designs": list((output_dir / "docs" / "agent_design").glob("[0-9][0-9]_*.design.json")),
    }
    return mapping.get(artifact_id, [])


def resolve_artifact(artifact_id: str, output_dir: Path) -> list[Path]:
    return [path for path in candidate_paths(artifact_id, output_dir) if path.exists()]


def add_check(checks: list[dict], name: str, ok: bool, details: str) -> None:
    checks.append({"name": name, "ok": ok, "details": details})


def response_text(artifacts: dict[str, list[Path]]) -> str:
    paths = artifacts.get("raw_response", [])
    if not paths:
        return ""
    return paths[0].read_text(encoding="utf-8", errors="ignore")


def read_many(paths: list[Path]) -> str:
    parts: list[str] = []
    for path in paths:
        parts.append(path.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(parts)


def check_dashboard_html(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    markers = [
        "overview",
        "agents",
        "issues",
        "roadmap",
        "agent",
        "backlog",
        "обзор",
        "агент",
        "проблем",
        "дорож",
    ]
    marker_hits = sum(1 for marker in markers if marker in text.lower())
    review_dense_markers = [
        'data-agent-card="',
        'data-block="evidence"',
        'data-block="criteria"',
        'data-block="contracts"',
        'data-block="backlog"',
        'data-block="patch-plan"',
    ]
    design_dense_markers = [
        'data-agent-card="',
        'data-block="business-function"',
        'data-block="control"',
        'data-block="mechanism"',
        'data-block="contracts"',
        'data-block="evaluation"',
        'data-block="delivery"',
    ]
    review_hits = sum(1 for marker in review_dense_markers if marker in text)
    design_hits = sum(1 for marker in design_dense_markers if marker in text)
    ok = ("<html" in text.lower() or "<!doctype html" in text.lower()) and len(text) >= 500 and marker_hits >= 2 and max(review_hits, design_hits) >= 5
    details = f"len={len(text)}, semantic_markers={marker_hits}, review_dense={review_hits}, design_dense={design_hits}"
    return ok, details


def validate_structured_agent(path: Path) -> tuple[bool, str]:
    payload = read_json(path)
    missing = STRUCTURED_AGENT_REQUIRED - set(payload)
    if missing:
        return False, f"{path.name}: missing_keys={sorted(missing)}"

    criteria = payload.get("criteria", [])
    if not isinstance(criteria, list) or len(criteria) != 10:
        return False, f"{path.name}: criteria_count={len(criteria) if isinstance(criteria, list) else 'invalid'}"

    evidence_points = payload.get("evidence_points", [])
    backlog = payload.get("backlog", [])
    patch_plan = payload.get("patch_plan", [])
    contracts = payload.get("contracts", {})

    if not isinstance(evidence_points, list) or len(evidence_points) < 3:
        return False, f"{path.name}: evidence_points={len(evidence_points) if isinstance(evidence_points, list) else 'invalid'}"
    if not isinstance(backlog, list) or len(backlog) < 3:
        return False, f"{path.name}: backlog={len(backlog) if isinstance(backlog, list) else 'invalid'}"
    if not isinstance(patch_plan, list) or len(patch_plan) != 3:
        return False, f"{path.name}: patch_plan={len(patch_plan) if isinstance(patch_plan, list) else 'invalid'}"
    if not isinstance(contracts, dict) or not contracts.get("current_contract") or not contracts.get("target_contract"):
        return False, f"{path.name}: contracts_incomplete"

    return True, path.name


def validate_structured_summary(path: Path, expected_agents: int) -> tuple[bool, str]:
    payload = read_json(path)
    missing = STRUCTURED_SUMMARY_REQUIRED - set(payload)
    if missing:
        return False, f"{path.name}: missing_keys={sorted(missing)}"

    maturity_rows = payload.get("maturity_matrix", {}).get("rows", [])
    contract_rows = payload.get("contract_matrix", {}).get("rows", [])
    if len(maturity_rows) != expected_agents:
        return False, f"{path.name}: maturity_rows={len(maturity_rows)} expected={expected_agents}"
    if not contract_rows:
        return False, f"{path.name}: contract_rows=0"
    return True, path.name


def validate_structured_design(path: Path) -> tuple[bool, str]:
    payload = read_json(path)
    missing = STRUCTURED_DESIGN_REQUIRED - set(payload)
    if missing:
        return False, f"{path.name}: missing_keys={sorted(missing)}"

    summary = payload.get("summary", {})
    if not isinstance(summary.get("readiness_score"), int):
        return False, f"{path.name}: readiness_score_missing"
    if not payload.get("control_spec", {}).get("sop"):
        return False, f"{path.name}: missing_control_sop"
    if not payload.get("mechanism_spec", {}).get("tools"):
        return False, f"{path.name}: missing_tools"
    if not payload.get("delivery_plan", {}).get("phases"):
        return False, f"{path.name}: missing_delivery_phases"
    if not payload.get("evaluation_plan", {}).get("scenarios"):
        return False, f"{path.name}: missing_eval_scenarios"
    return True, path.name


def validate_structured_design_summary(path: Path, expected_agents: int) -> tuple[bool, str]:
    payload = read_json(path)
    missing = STRUCTURED_DESIGN_SUMMARY_REQUIRED - set(payload)
    if missing:
        return False, f"{path.name}: missing_keys={sorted(missing)}"

    contract_rows = payload.get("contract_matrix", {}).get("rows", [])
    phases = payload.get("implementation_phases", [])
    if len(contract_rows) != expected_agents:
        return False, f"{path.name}: contract_rows={len(contract_rows)} expected={expected_agents}"
    if not phases:
        return False, f"{path.name}: implementation_phases=0"
    return True, path.name


def check_review_content(manifest: dict, artifacts: dict[str, list[Path]]) -> list[dict]:
    checks: list[dict] = []
    audit_paths = artifacts.get("agent_audits", [])
    combined = read_many(audit_paths)
    evidence_hits = len(EVIDENCE_RE.findall(combined))
    add_check(
        checks,
        "review_evidence_refs",
        evidence_hits >= 3,
        f"evidence_refs={evidence_hits}",
    )

    summary_paths = artifacts.get("audit_summary", [])
    if summary_paths:
        summary_len = len(summary_paths[0].read_text(encoding="utf-8", errors="ignore").strip())
        add_check(checks, "review_summary_nonempty", summary_len > 20, f"chars={summary_len}")

    structured_paths = artifacts.get("structured_audits", [])
    structured_results = [validate_structured_agent(path) for path in structured_paths]
    if structured_results:
        ok = all(result[0] for result in structured_results)
        details = "; ".join(result[1] for result in structured_results)
        add_check(checks, "structured_audit_schema", ok, details)

    structured_summary_paths = artifacts.get("structured_summary", [])
    if structured_summary_paths:
        ok, details = validate_structured_summary(structured_summary_paths[0], len(structured_paths))
        add_check(checks, "structured_summary_schema", ok, details)

    if manifest["id"] == "functional-review-r1":
        structured_text = read_many(structured_paths) if structured_paths else ""
        text = (combined + "\n" + structured_text + "\n" + response_text(artifacts)).lower()
        category_hits = 0
        matched: list[str] = []
        for category, patterns in FINDING_PATTERNS.items():
            if any(re.search(pattern, text) for pattern in patterns):
                category_hits += 1
                matched.append(category)
        add_check(
            checks,
            "expected_findings_coverage",
            category_hits >= 5,
            f"matched={category_hits}; categories={','.join(matched)}",
        )

    return checks


def check_design_content(artifacts: dict[str, list[Path]]) -> list[dict]:
    checks: list[dict] = []
    design_paths = artifacts.get("agent_designs", [])
    combined = read_many(design_paths)

    required_sections = ["idef0", "contracts", "evaluation plan", "delivery plan", "control", "mechanism"]
    section_hits = sum(1 for section in required_sections if section in combined.lower())
    add_check(checks, "design_markdown_sections", section_hits >= 4, f"section_hits={section_hits}")

    summary_paths = artifacts.get("design_summary", [])
    if summary_paths:
        summary_len = len(summary_paths[0].read_text(encoding="utf-8", errors="ignore").strip())
        add_check(checks, "design_summary_nonempty", summary_len > 20, f"chars={summary_len}")

    structured_paths = artifacts.get("structured_designs", [])
    structured_results = [validate_structured_design(path) for path in structured_paths]
    if structured_results:
        ok = all(result[0] for result in structured_results)
        details = "; ".join(result[1] for result in structured_results)
        add_check(checks, "structured_design_schema", ok, details)

    structured_summary_paths = artifacts.get("structured_design_summary", [])
    if structured_summary_paths:
        ok, details = validate_structured_design_summary(structured_summary_paths[0], len(structured_paths))
        add_check(checks, "structured_design_summary_schema", ok, details)

    return checks


def check_content(manifest: dict, artifacts: dict[str, list[Path]]) -> list[dict]:
    checks: list[dict] = []
    raw_paths = artifacts.get("raw_response", [])
    if raw_paths:
        raw_text = raw_paths[0].read_text(encoding="utf-8", errors="ignore").strip()
        add_check(checks, "raw_response_nonempty", len(raw_text) > 20, f"chars={len(raw_text)}")
        if "ru" in set(manifest.get("tags", [])):
            has_cyrillic = bool(re.search(r"[А-Яа-яЁё]", raw_text))
            add_check(checks, "response_has_cyrillic", has_cyrillic, "cyrillic_detected" if has_cyrillic else "missing")

    dashboard_paths = artifacts.get("dashboard_html", [])
    if dashboard_paths:
        ok, details = check_dashboard_html(dashboard_paths[0])
        add_check(checks, "dashboard_html_smoke", ok, details)

    if "review" in set(manifest.get("tags", [])) and artifacts.get("agent_audits"):
        checks.extend(check_review_content(manifest, artifacts))
    if "design" in set(manifest.get("tags", [])) and artifacts.get("agent_designs"):
        checks.extend(check_design_content(artifacts))

    return checks


def main() -> int:
    args = parse_args()
    iteration_dir = Path(args.iteration_dir).resolve()
    eval_dirs = sorted(path for path in iteration_dir.iterdir() if path.is_dir() and path.name.startswith("eval-"))

    report: dict[str, dict] = {}
    has_errors = False

    for eval_dir in eval_dirs:
        eval_report: dict[str, dict] = {}
        for config_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            manifest_path = config_dir / "run-manifest.json"
            if not manifest_path.exists():
                continue

            manifest = read_json(manifest_path)
            output_dir = Path(manifest["output_dir"])
            expectations = manifest.get("artifact_expectations", {})
            required = expectations.get("required", ["raw_response"])
            forbidden = expectations.get("forbidden", [])

            artifacts: dict[str, list[Path]] = {}
            artifact_results: dict[str, dict] = {}
            missing: list[str] = []
            unexpected: list[str] = []

            for artifact_id in sorted(set(required + forbidden)):
                resolved = resolve_artifact(artifact_id, output_dir)
                artifacts[artifact_id] = resolved

            for artifact_id in required:
                resolved = artifacts.get(artifact_id, [])
                ok = bool(resolved)
                artifact_results[artifact_id] = {
                    "ok": ok,
                    "paths": [str(path) for path in resolved],
                }
                if not ok:
                    missing.append(artifact_id)

            for artifact_id in forbidden:
                resolved = artifacts.get(artifact_id, [])
                ok = not resolved
                artifact_results[artifact_id] = {
                    "ok": ok,
                    "paths": [str(path) for path in resolved],
                }
                if resolved:
                    unexpected.append(artifact_id)

            content_checks = check_content(manifest, artifacts)
            failed_content = [check["name"] for check in content_checks if not check["ok"]]

            eval_report[config_dir.name] = {
                "ok": not missing and not unexpected and not failed_content,
                "missing": missing,
                "unexpected": unexpected,
                "checks": artifact_results,
                "content_checks": content_checks,
            }
            has_errors = has_errors or bool(missing or unexpected or failed_content)

        if eval_report:
            report[eval_dir.name] = eval_report

    payload = {
        "iteration_dir": str(iteration_dir),
        "ok": not has_errors,
        "results": report,
    }
    output_path = iteration_dir / "artifact-check.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote artifact report to {output_path}")
    if has_errors:
        for eval_name, eval_report in report.items():
            for config_name, config_report in eval_report.items():
                if config_report["missing"]:
                    print(f"MISSING {eval_name}/{config_name}: {', '.join(config_report['missing'])}")
                if config_report["unexpected"]:
                    print(f"UNEXPECTED {eval_name}/{config_name}: {', '.join(config_report['unexpected'])}")
                failed_content = [check["name"] for check in config_report["content_checks"] if not check["ok"]]
                if failed_content:
                    print(f"CONTENT {eval_name}/{config_name}: {', '.join(failed_content)}")
        return 1

    print("Artifact validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
