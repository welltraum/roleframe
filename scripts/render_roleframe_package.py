#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from render_audit_package import (
    TEMPLATE_PATH,
    ValidationError,
    ensure,
    html_list_items,
    render_code_block,
    render_link_pill,
    render_overview_cards,
    render_package as render_review_package,
    unit_kind_label,
    unit_noun,
    write_text,
)


DESIGN_AGENT_REQUIRED = {
    "metadata",
    "summary",
    "business_function",
    "idef0",
    "control_spec",
    "mechanism_spec",
    "governance",
    "contracts",
    "dependencies",
    "evaluation_plan",
    "delivery_plan",
}

DESIGN_SUMMARY_REQUIRED = {
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
    parser = argparse.ArgumentParser(description="Render a RoleFrame design or review package from structured JSON.")
    parser.add_argument("--kind", choices=["review", "design"], required=True, help="Package kind to render.")
    parser.add_argument("--input", required=True, help="Directory with structured RoleFrame package files.")
    parser.add_argument("--output", required=True, help="Directory where markdown and dashboard views are written.")
    parser.add_argument("--check", action="store_true", help="Validate the package and exit without writing files.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sentence_count(text: str) -> int:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    return len(parts) if parts else 0


def validate_budget(name: str, text: str, *, min_sentences: int | None = None, max_sentences: int | None = None) -> None:
    count = sentence_count(text)
    if min_sentences is not None:
        ensure(count >= min_sentences, f"{name} must have at least {min_sentences} sentence(s)")
    if max_sentences is not None:
        ensure(count <= max_sentences, f"{name} must have at most {max_sentences} sentence(s)")


def validate_design_agent(path: Path, payload: dict) -> None:
    missing = DESIGN_AGENT_REQUIRED - set(payload)
    ensure(not missing, f"{path.name} is missing keys: {sorted(missing)}")

    metadata = payload["metadata"]
    ensure(metadata.get("unit_kind") in {"agent", "pack", "workflow"}, f"{path.name}: metadata.unit_kind must be agent, pack, or workflow")
    for field in ["name", "language", "source_context", "designed_at"]:
        ensure(isinstance(metadata.get(field), str) and metadata[field], f"{path.name}: metadata.{field} is required")

    summary = payload["summary"]
    ensure(isinstance(summary.get("readiness_score"), int) and 0 <= summary["readiness_score"] <= 100, f"{path.name}: summary.readiness_score must be 0..100")
    for field in ["readiness_level", "verdict", "primary_risk"]:
        ensure(isinstance(summary.get(field), str) and summary[field], f"{path.name}: summary.{field} is required")
    validate_budget(f"{path.name}: summary.verdict", summary["verdict"], min_sentences=2, max_sentences=4)

    business_function = payload["business_function"]
    ensure(isinstance(business_function.get("goal"), str) and business_function["goal"], f"{path.name}: business_function.goal is required")
    ensure(isinstance(business_function.get("consumer"), str) and business_function["consumer"], f"{path.name}: business_function.consumer is required")
    for field in ["success_criteria", "in_scope", "out_of_scope"]:
        ensure(isinstance(business_function.get(field), list) and business_function[field], f"{path.name}: business_function.{field} must be a non-empty list")

    idef0 = payload["idef0"]
    for quadrant in ["input", "control", "mechanism", "output"]:
        ensure(isinstance(idef0.get(quadrant), str) and idef0[quadrant], f"{path.name}: idef0.{quadrant} is required")
        validate_budget(f"{path.name}: idef0.{quadrant}", idef0[quadrant], min_sentences=1, max_sentences=2)

    control = payload["control_spec"]
    ensure(isinstance(control.get("role"), str) and control["role"], f"{path.name}: control_spec.role is required")
    ensure(isinstance(control.get("sop"), list) and control["sop"], f"{path.name}: control_spec.sop must be a non-empty list")
    ensure(isinstance(control.get("constraints"), list) and control["constraints"], f"{path.name}: control_spec.constraints must be a non-empty list")

    mechanism = payload["mechanism_spec"]
    for field in ["memory_strategy", "runtime_loop", "error_handling"]:
        ensure(isinstance(mechanism.get(field), str) and mechanism[field], f"{path.name}: mechanism_spec.{field} is required")
    ensure(isinstance(mechanism.get("tools"), list) and mechanism["tools"], f"{path.name}: mechanism_spec.tools must be a non-empty list")
    for index, tool in enumerate(mechanism["tools"], start=1):
        for field in ["name", "purpose", "failure_mode"]:
            ensure(isinstance(tool.get(field), str) and tool[field], f"{path.name}: mechanism_spec.tools[{index}].{field} is required")

    contracts = payload["contracts"]
    for field in ["consumer", "input_contract", "output_contract", "failure_contract"]:
        ensure(isinstance(contracts.get(field), str) and contracts[field], f"{path.name}: contracts.{field} is required")

    dependencies = payload["dependencies"]
    ensure(isinstance(dependencies, list) and dependencies, f"{path.name}: dependencies must be a non-empty list")
    for index, item in enumerate(dependencies, start=1):
        for field in ["name", "type", "reason", "risk"]:
            ensure(isinstance(item.get(field), str) and item[field], f"{path.name}: dependencies[{index}].{field} is required")

    evaluation = payload["evaluation_plan"]
    for field in ["scenarios", "metrics", "regression"]:
        ensure(isinstance(evaluation.get(field), list) and evaluation[field], f"{path.name}: evaluation_plan.{field} must be a non-empty list")

    governance = payload["governance"]
    ensure(isinstance(governance.get("owner_boundary"), str) and governance["owner_boundary"], f"{path.name}: governance.owner_boundary is required")
    ensure(isinstance(governance.get("routes"), list) and governance["routes"], f"{path.name}: governance.routes must be a non-empty list")
    for index, item in enumerate(governance["routes"], start=1):
        for field in ["name", "consumer", "contract", "risk"]:
            ensure(isinstance(item.get(field), str) and item[field], f"{path.name}: governance.routes[{index}].{field} is required")
    for field in ["owned_surfaces", "proof_surfaces", "deployment_visibility", "rollout", "preparedness"]:
        ensure(isinstance(governance.get(field), list) and governance[field], f"{path.name}: governance.{field} must be a non-empty list")

    delivery = payload["delivery_plan"]
    for field in ["observability", "change_management"]:
        ensure(isinstance(delivery.get(field), list) and delivery[field], f"{path.name}: delivery_plan.{field} must be a non-empty list")
    ensure(isinstance(delivery.get("phases"), list) and delivery["phases"], f"{path.name}: delivery_plan.phases must be a non-empty list")
    for index, phase in enumerate(delivery["phases"], start=1):
        for field in ["title", "description"]:
            ensure(isinstance(phase.get(field), str) and phase[field], f"{path.name}: delivery_plan.phases[{index}].{field} is required")


def validate_design_summary(path: Path, payload: dict, agents: list[dict]) -> None:
    missing = DESIGN_SUMMARY_REQUIRED - set(payload)
    ensure(not missing, f"{path.name} is missing keys: {sorted(missing)}")
    ensure(payload["language"] in {"ru", "en"}, f"{path.name}: language must be ru or en")
    ensure(isinstance(payload["overview_cards"], list) and 3 <= len(payload["overview_cards"]) <= 4, f"{path.name}: overview_cards must contain 3..4 items")
    ensure(isinstance(payload["critical_risks"], list) and 3 <= len(payload["critical_risks"]) <= 5, f"{path.name}: critical_risks must contain 3..5 items")
    architecture = payload["architecture"]
    for field in ["heading", "text", "mermaid"]:
        ensure(isinstance(architecture.get(field), str) and architecture[field], f"{path.name}: architecture.{field} is required")
    contract_matrix = payload["contract_matrix"]
    ensure(isinstance(contract_matrix.get("columns"), list) and contract_matrix["columns"], f"{path.name}: contract_matrix.columns must be non-empty")
    ensure(isinstance(contract_matrix.get("rows"), list) and len(contract_matrix["rows"]) == len(agents), f"{path.name}: contract_matrix.rows must match agent count")
    ensure(isinstance(payload["implementation_phases"], list) and payload["implementation_phases"], f"{path.name}: implementation_phases must be non-empty")
    methodology = payload.get("methodology", {})
    if methodology:
        ensure(isinstance(methodology.get("lead"), str) and methodology["lead"], f"{path.name}: methodology.lead is required when methodology block is present")
        ensure(isinstance(methodology.get("summary_blocks"), list) and methodology["summary_blocks"], f"{path.name}: methodology.summary_blocks must be non-empty")


def load_design_package(input_dir: Path) -> tuple[list[dict], dict]:
    agent_paths = sorted(input_dir.glob("[0-9][0-9]_*.design.json"))
    summary_path = input_dir / "summary.design.json"
    ensure(agent_paths, f"No structured design JSON files found in {input_dir}")
    ensure(summary_path.exists(), f"{summary_path.name} is required when design JSON files exist")

    agents = [read_json(path) for path in agent_paths]
    for path, payload in zip(agent_paths, agents):
        validate_design_agent(path, payload)
    summary = read_json(summary_path)
    validate_design_summary(summary_path, summary, agents)
    return agents, summary


def prepare_design_agents(agents: list[dict]) -> list[dict]:
    prepared = []
    for index, agent in enumerate(agents, start=1):
        stem = f"{index:02d}_{agent['metadata']['name']}"
        prepared.append(
            {
                **agent,
                "metadata": {
                    **agent["metadata"],
                    "file_stem": stem,
                },
            }
        )
    return prepared


def render_design_markdown_agent(agent: dict) -> str:
    language = agent["metadata"]["language"]
    in_scope_label = "В scope" if language == "ru" else "In scope"
    out_of_scope_label = "Вне scope" if language == "ru" else "Out of scope"
    readiness_label = "Готовность" if language == "ru" else "Readiness"
    constraints_label = "Ограничения" if language == "ru" else "Constraints"
    contracts_label = "Контракты" if language == "ru" else "Contracts"
    consumer_label = "Потребитель" if language == "ru" else "Consumer"
    input_label = "Вход" if language == "ru" else "Input"
    output_label = "Выход" if language == "ru" else "Output"
    failure_label = "Сбой" if language == "ru" else "Failure"
    dependencies_label = "Зависимости" if language == "ru" else "Dependencies"
    evaluation_label = "План eval" if language == "ru" else "Evaluation plan"
    scenarios_label = "Сценарии" if language == "ru" else "Scenarios"
    metrics_label = "Метрики" if language == "ru" else "Metrics"
    regression_label = "Регрессия" if language == "ru" else "Regression"
    delivery_label = "План внедрения" if language == "ru" else "Delivery plan"
    observability_label = "Наблюдаемость" if language == "ru" else "Observability"
    change_mgmt_label = "Управление изменениями" if language == "ru" else "Change management"
    lines = [f"# Проектирование: unit `{agent['metadata']['name']}`" if language == "ru" else f"# Design: unit `{agent['metadata']['name']}`", ""]
    lines.extend(
        [
            "## Краткий вердикт" if language == "ru" else "## Verdict",
            "",
            f"{readiness_label}: **{agent['summary']['readiness_score']}/100**, {agent['summary']['readiness_level']}",
            "",
            agent["summary"]["verdict"],
            "",
            "## Профиль" if language == "ru" else "## Profile",
            "",
            f"`{unit_kind_label(agent['metadata']['unit_kind'], language)}`",
            "",
            "## Граница" if language == "ru" else "## Boundary",
            "",
            f"- **{'Цель' if language == 'ru' else 'Goal'}**: {agent['business_function']['goal']}",
            f"- **{'Потребитель' if language == 'ru' else 'Consumer'}**: {agent['business_function']['consumer']}",
            "",
            "### Критерии успеха" if language == "ru" else "### Success criteria",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in agent["business_function"]["success_criteria"])
    lines.extend(["", f"### {in_scope_label}", ""])
    lines.extend(f"- {item}" for item in agent["business_function"]["in_scope"])
    lines.extend(["", f"### {out_of_scope_label}", ""])
    lines.extend(f"- {item}" for item in agent["business_function"]["out_of_scope"])
    lines.extend(["", "## IDEF0", ""])
    for quadrant in ["input", "control", "mechanism", "output"]:
        lines.append(f"- **{quadrant.title()}**: {agent['idef0'][quadrant]}")
    lines.extend(["", "## Control", ""])
    lines.append(f"- **{'Роль' if language == 'ru' else 'Role'}**: {agent['control_spec']['role']}")
    lines.append("")
    lines.append("### SOP")
    lines.append("")
    lines.extend(f"{index}. {item}" for index, item in enumerate(agent["control_spec"]["sop"], start=1))
    lines.extend(["", f"### {constraints_label}", ""])
    lines.extend(f"- {item}" for item in agent["control_spec"]["constraints"])
    lines.extend(["", "## Mechanism", ""])
    lines.append(
        "| Инструмент | Назначение | Режим сбоя |" if language == "ru" else "| Tool | Purpose | Failure mode |"
    )
    lines.append("|---|---|---|")
    for tool in agent["mechanism_spec"]["tools"]:
        lines.append(f"| `{tool['name']}` | {tool['purpose']} | {tool['failure_mode']} |")
    lines.extend(
        [
            "",
            f"- **{'Memory strategy' if language == 'en' else 'Стратегия памяти'}**: {agent['mechanism_spec']['memory_strategy']}",
            f"- **{'Runtime loop' if language == 'en' else 'Runtime loop'}**: {agent['mechanism_spec']['runtime_loop']}",
            f"- **{'Error handling' if language == 'en' else 'Обработка ошибок'}**: {agent['mechanism_spec']['error_handling']}",
            "",
            "## Governance",
            "",
            f"- **Owner boundary**: {agent['governance']['owner_boundary']}",
            "",
            "### Routes",
            "",
            "| Route | Consumer | Contract | Risk |",
            "|---|---|---|---|",
        ]
    )
    for item in agent["governance"]["routes"]:
        lines.append(f"| `{item['name']}` | `{item['consumer']}` | {item['contract']} | {item['risk']} |")
    for field, label in [
        ("owned_surfaces", "Owned surfaces"),
        ("proof_surfaces", "Proof surfaces"),
        ("deployment_visibility", "Deployment visibility"),
        ("rollout", "Rollout"),
        ("preparedness", "Preparedness"),
    ]:
        lines.extend(["", f"### {label}", ""])
        lines.extend(f"- {item}" for item in agent["governance"][field])
    lines.extend(
        [
            "",
            f"## {contracts_label}",
            "",
            f"{consumer_label}: `{agent['contracts']['consumer']}`",
            "",
            f"### {input_label}",
            "",
            "```text",
            agent["contracts"]["input_contract"].strip(),
            "```",
            "",
            f"### {output_label}",
            "",
            "```text",
            agent["contracts"]["output_contract"].strip(),
            "```",
            "",
            f"### {failure_label}",
            "",
            "```text",
            agent["contracts"]["failure_contract"].strip(),
            "```",
            "",
            f"## {dependencies_label}",
            "",
            "| Название | Тип | Причина | Риск |" if language == "ru" else "| Name | Type | Reason | Risk |",
            "|---|---|---|---|",
        ]
    )
    for item in agent["dependencies"]:
        lines.append(f"| {item['name']} | {item['type']} | {item['reason']} | {item['risk']} |")
    lines.extend(["", f"## {evaluation_label}", ""])
    lines.append(f"### {scenarios_label}")
    lines.append("")
    lines.extend(f"- {item}" for item in agent["evaluation_plan"]["scenarios"])
    lines.extend(["", f"### {metrics_label}", ""])
    lines.extend(f"- {item}" for item in agent["evaluation_plan"]["metrics"])
    lines.extend(["", f"### {regression_label}", ""])
    lines.extend(f"- {item}" for item in agent["evaluation_plan"]["regression"])
    lines.extend(["", f"## {delivery_label}", ""])
    for phase in agent["delivery_plan"]["phases"]:
        lines.append(f"### {phase['title']}")
        lines.append("")
        lines.append(phase["description"])
        lines.append("")
    lines.append(f"### {observability_label}")
    lines.append("")
    lines.extend(f"- {item}" for item in agent["delivery_plan"]["observability"])
    lines.extend(["", f"### {change_mgmt_label}", ""])
    lines.extend(f"- {item}" for item in agent["delivery_plan"]["change_management"])
    lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_design_markdown_summary(agents: list[dict], summary: dict) -> str:
    language = summary["language"]
    lines = [
        "# Проектирование units (методология RoleFrame)" if language == "ru" else "# Unit design (RoleFrame methodology)",
        "",
        summary["overall_verdict"],
        "",
        "## Файлы" if language == "ru" else "## Files",
        "",
    ]
    for agent in agents:
        lines.append(f"- `{agent['metadata']['file_stem']}.md`")
    lines.extend(
        [
            "",
            "## Сводка" if language == "ru" else "## Summary",
            "",
            "| Unit | Готовность | Уровень | Основной риск | Первая фаза |"
            if language == "ru"
            else "| Unit | Readiness | Level | Primary risk | First phase |",
            "|---|---:|---|---|---|",
        ]
    )
    for agent in agents:
        lines.append(
            f"| `{agent['metadata']['name']}` | {agent['summary']['readiness_score']}/100 | {agent['summary']['readiness_level']} | {agent['summary']['primary_risk']} | {agent['delivery_plan']['phases'][0]['title']} |"
        )
    lines.extend(["", "## Критические риски" if language == "ru" else "## Critical risks", ""])
    lines.extend(f"- {item}" for item in summary["critical_risks"])
    lines.append("")
    return "\n".join(lines)


def render_design_score_rows(agents: list[dict]) -> str:
    rows = []
    for agent in agents:
        score = agent["summary"]["readiness_score"]
        bar = min(100, score)
        color = "bg-rose-500" if score < 50 else ("bg-amber-500" if score < 75 else "bg-emerald-600")
        rows.append(
            "<div>"
            f'<div class="flex justify-between text-sm mb-1"><span class="font-semibold">{html.escape(agent["metadata"]["name"])}</span><span>{score}/100, {html.escape(agent["summary"]["readiness_level"])}</span></div>'
            f'<div class="w-full h-3 bg-stone-200 rounded-full overflow-hidden"><div class="h-3 {color} score-bar" style="width:{bar}%"></div></div>'
            f'<div class="text-xs text-slate-500 mt-1">{html.escape(agent["summary"]["primary_risk"])}</div>'
            "</div>"
        )
    return "\n".join(rows)


def render_design_methodology_links(output_dir: Path, language: str) -> str:
    summary_label = "Открыть сводку дизайна" if language == "ru" else "Open design summary"
    design_label = "Открыть design schema" if language == "ru" else "Open design schema"
    methodology_label = "Открыть методологию" if language == "ru" else "Open methodology"
    return "\n".join(
        [
            render_link_pill(output_dir, output_dir / "README.md", summary_label),
            render_link_pill(output_dir, "references/structured-design.md", design_label),
            render_link_pill(output_dir, "references/methodology.md", methodology_label),
        ]
    )


def render_design_methodology_blocks(summary: dict) -> str:
    language = summary["language"]
    methodology = summary.get("methodology") or {}
    blocks = methodology.get("summary_blocks") or [
        {
            "title": "Что уже зафиксировано" if language == "ru" else "What is fixed",
            "items": [
                "boundary, consumer и profile" if language == "ru" else "boundary, consumer, and profile",
                "Control vs Mechanism split" if language == "ru" else "control vs mechanism split",
                "typed contracts и governance" if language == "ru" else "typed contracts and governance",
            ],
        },
        {
            "title": "Что ещё внедрить" if language == "ru" else "What still needs implementation",
            "items": [
                "runtime orchestration и route adapters" if language == "ru" else "runtime orchestration and route adapters",
                "eval-сценарии, proof surfaces и regression loop" if language == "ru" else "eval scenarios, proof surfaces, and regression loop",
                "наблюдаемость, rollout-checks и preparedness" if language == "ru" else "observability, rollout checks, and preparedness",
            ],
        },
    ]
    html_blocks = []
    for block in blocks:
        html_blocks.append(
            '<div class="rounded-2xl border border-stone-200 bg-stone-50 p-4">'
            f'<div class="font-semibold mb-2">{html.escape(block["title"])}</div>'
            f'<ul class="list-disc pl-5 space-y-1">{html_list_items(block["items"])}</ul>'
            "</div>"
        )
    return "\n".join(html_blocks)


def render_design_contract_matrix(summary: dict) -> tuple[str, str]:
    language = summary["language"]
    header = "<th>Unit</th>"
    header += "".join(f"<th>{html.escape(column)}</th>" for column in summary["contract_matrix"]["columns"])
    rows = []
    for row in summary["contract_matrix"]["rows"]:
        cells = "".join(
            f'<td><span class="chip chip-neutral">{html.escape(cell["status"])}</span><div class="text-xs text-slate-500 mt-1">{html.escape(cell["note"])}</div></td>'
            for cell in row["cells"]
        )
        rows.append(f"<tr><td><span class=\"mono\">{html.escape(row['agent'])}</span></td>{cells}</tr>")
    return header, "\n".join(rows)


def derive_design_matrix(agents: list[dict], language: str) -> tuple[str, str]:
    headers = [
        "Unit",
        "Граница" if language == "ru" else "Boundary",
        "Control",
        "Mechanism",
        "Eval",
        "Delivery",
    ]
    header = "".join(f"<th>{html.escape(item)}</th>" for item in headers)
    rows: list[str] = []
    status_labels = {
        "fixed": "зафиксировано" if language == "ru" else "fixed",
        "defined": "определено" if language == "ru" else "defined",
        "planned": "запланировано" if language == "ru" else "planned",
        "draft": "черновик" if language == "ru" else "draft",
        "missing": "отсутствует" if language == "ru" else "missing",
    }
    for agent in agents:
        values = [
            status_labels["fixed"] if agent["business_function"]["goal"] else status_labels["draft"],
            status_labels["defined"] if agent["control_spec"]["sop"] else status_labels["draft"],
            status_labels["defined"] if agent["mechanism_spec"]["tools"] else status_labels["draft"],
            status_labels["planned"] if agent["evaluation_plan"]["scenarios"] else status_labels["missing"],
            status_labels["planned"] if agent["delivery_plan"]["phases"] else status_labels["missing"],
        ]
        row_values = "".join(f"<td>{html.escape(value)}</td>" for value in values)
        rows.append(f"<tr><td><span class=\"mono\">{html.escape(agent['metadata']['name'])}</span></td>{row_values}</tr>")
    return header, "\n".join(rows)


def render_design_roadmap(summary: dict) -> str:
    return "\n".join(
        [
            '<div class="rounded-2xl border border-stone-200 p-4">'
            f'<div class="font-semibold">{html.escape(item["title"])}</div>'
            f'<p class="text-slate-600 mt-1">{html.escape(item["description"])}</p>'
            "</div>"
            for item in summary["implementation_phases"]
        ]
    )


def render_design_critical_risks(summary: dict) -> str:
    return "\n".join(f"<p><strong>{index}.</strong> {html.escape(item)}</p>" for index, item in enumerate(summary["critical_risks"], start=1))


def render_design_agent_card(agent: dict, output_dir: Path) -> str:
    language = agent["metadata"]["language"]
    badge_class = "badge-danger" if agent["summary"]["readiness_score"] < 50 else ("badge-warn" if agent["summary"]["readiness_score"] < 75 else "badge-good")
    tool_rows = "\n".join(
        [
            "<tr>"
            f"<td>{html.escape(item['name'])}</td>"
            f"<td>{html.escape(item['purpose'])}</td>"
            f"<td>{html.escape(item['failure_mode'])}</td>"
            "</tr>"
            for item in agent["mechanism_spec"]["tools"]
        ]
    )
    dependency_rows = "\n".join(
        [
            "<tr>"
            f"<td>{html.escape(item['name'])}</td>"
            f"<td>{html.escape(item['type'])}</td>"
            f"<td>{html.escape(item['reason'])}</td>"
            f"<td>{html.escape(item['risk'])}</td>"
            "</tr>"
            for item in agent["dependencies"]
        ]
    )
    phases = "\n".join(
        [
            '<div class="rounded-2xl border border-stone-200 p-4">'
            f'<div class="font-semibold mb-1">{html.escape(item["title"])}</div>'
            f'<p class="text-sm text-slate-600">{html.escape(item["description"])}</p>'
            "</div>"
            for item in agent["delivery_plan"]["phases"]
        ]
    )
    source_link = render_link_pill(output_dir, str(output_dir / f"{agent['metadata']['file_stem']}.md"), "Полный design" if language == "ru" else "Full design")
    tool_label = "Инструмент" if language == "ru" else "Tool"
    purpose_label = "Назначение" if language == "ru" else "Purpose"
    failure_mode_label = "Режим сбоя" if language == "ru" else "Failure mode"
    name_label = "Название" if language == "ru" else "Name"
    type_label = "Тип" if language == "ru" else "Type"
    reason_label = "Причина" if language == "ru" else "Reason"
    risk_label = "Риск" if language == "ru" else "Risk"
    memory_label = "Память" if language == "ru" else "Memory"
    errors_label = "Ошибки" if language == "ru" else "Errors"
    constraints_label = "Ограничения" if language == "ru" else "Constraints"
    input_contract_label = "Входной контракт" if language == "ru" else "Input contract"
    output_failure_label = "Выходной и аварийный контракт" if language == "ru" else "Output and failure contract"
    scenarios_label = "Сценарии" if language == "ru" else "Scenarios"
    metrics_label = "Метрики" if language == "ru" else "Metrics"
    regression_label = "Регрессия" if language == "ru" else "Regression"
    observability_label = "Наблюдаемость" if language == "ru" else "Observability"
    change_mgmt_label = "Управление изменениями" if language == "ru" else "Change management"
    governance_rows = "\n".join(
        [
            "<tr>"
            f"<td><span class=\"mono\">{html.escape(item['name'])}</span></td>"
            f"<td><span class=\"mono\">{html.escape(item['consumer'])}</span></td>"
            f"<td>{html.escape(item['contract'])}</td>"
            f"<td>{html.escape(item['risk'])}</td>"
            "</tr>"
            for item in agent["governance"]["routes"]
        ]
    )
    return (
        f'<article class="panel rounded-3xl p-6 space-y-5" data-unit-card="{html.escape(agent["metadata"]["name"])}">'
        '<div class="flex flex-wrap items-center justify-between gap-3">'
        f'<div><h2 class="text-xl font-bold">{html.escape(agent["metadata"]["name"])}</h2>'
        f'<p class="text-sm text-slate-500">{html.escape(agent["summary"]["primary_risk"])}</p></div>'
        f'<div class="flex items-center gap-2"><span class="{badge_class} rounded-full px-3 py-1 text-sm font-bold">{agent["summary"]["readiness_score"]}/100</span>'
        f'<span class="chip chip-neutral">{html.escape(agent["summary"]["readiness_level"])}</span>'
        f'<span class="chip chip-neutral">{html.escape(unit_kind_label(agent["metadata"]["unit_kind"], language))}</span></div>'
        "</div>"
        f'<div class="flex flex-wrap gap-2" data-block="sources">{source_link}</div>'
        '<div class="rounded-2xl bg-stone-50 border border-stone-200 p-4" data-block="verdict">'
        f'<div class="font-semibold mb-2">{"Краткий вердикт" if language == "ru" else "Short verdict"}</div>'
        f'<p class="text-sm">{html.escape(agent["summary"]["verdict"])}</p>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="boundary">'
        f'<div class="font-semibold mb-3">{"Граница" if language == "ru" else "Boundary"}</div>'
        f'<div class="text-sm"><strong>{"Цель" if language == "ru" else "Goal"}:</strong> {html.escape(agent["business_function"]["goal"])}</div>'
        f'<div class="text-sm mt-2"><strong>{"Потребитель" if language == "ru" else "Consumer"}:</strong> {html.escape(agent["business_function"]["consumer"])}</div>'
        f'<ul class="list-disc pl-5 mt-3 space-y-1 text-sm">{html_list_items(agent["business_function"]["success_criteria"])}</ul>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="idef0">'
        '<div class="font-semibold mb-3">IDEF0</div>'
        f'<div class="space-y-2 text-sm"><div><strong>Input:</strong> {html.escape(agent["idef0"]["input"])}</div>'
        f'<div><strong>Control:</strong> {html.escape(agent["idef0"]["control"])}</div>'
        f'<div><strong>Mechanism:</strong> {html.escape(agent["idef0"]["mechanism"])}</div>'
        f'<div><strong>Output:</strong> {html.escape(agent["idef0"]["output"])}</div></div>'
        "</div>"
        '<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">'
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="control">'
        f'<div class="font-semibold mb-3">{"Control"}</div>'
        f'<div class="text-sm mb-2"><strong>{"Роль" if language == "ru" else "Role"}:</strong> {html.escape(agent["control_spec"]["role"])}</div>'
        f'<div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">SOP</div><ul class="list-disc pl-5 space-y-1 text-sm">{html_list_items(agent["control_spec"]["sop"])}</ul>'
        f'<div class="text-xs uppercase tracking-[0.14em] text-slate-400 mt-4 mb-2">{constraints_label}</div><ul class="list-disc pl-5 space-y-1 text-sm">{html_list_items(agent["control_spec"]["constraints"])}</ul>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="mechanism">'
        f'<div class="font-semibold mb-3">{"Mechanism"}</div>'
        f'<div class="overflow-x-auto"><table class="w-full text-sm data-table"><thead><tr><th>{tool_label}</th><th>{purpose_label}</th><th>{failure_mode_label}</th></tr></thead>'
        f"<tbody>{tool_rows}</tbody></table></div>"
        f'<div class="text-sm mt-3"><strong>{memory_label}:</strong> {html.escape(agent["mechanism_spec"]["memory_strategy"])}</div>'
        f'<div class="text-sm mt-2"><strong>Runtime:</strong> {html.escape(agent["mechanism_spec"]["runtime_loop"])}</div>'
        f'<div class="text-sm mt-2"><strong>{errors_label}:</strong> {html.escape(agent["mechanism_spec"]["error_handling"])}</div>'
        "</div>"
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="governance">'
        f'<div class="font-semibold mb-3">{"Governance"}</div>'
        f'<div class="text-sm mb-3"><strong>{"Owner boundary"}:</strong> {html.escape(agent["governance"]["owner_boundary"])}</div>'
        '<div class="overflow-x-auto"><table class="w-full text-sm data-table"><thead><tr><th>Route</th><th>Consumer</th><th>Contract</th><th>Risk</th></tr></thead>'
        f"<tbody>{governance_rows}</tbody></table></div>"
        f'<div class="grid grid-cols-1 lg:grid-cols-5 gap-4 mt-4 text-sm">'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{"Owned surfaces"}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["governance"]["owned_surfaces"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{"Proof surfaces"}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["governance"]["proof_surfaces"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{"Deployment visibility"}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["governance"]["deployment_visibility"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{"Rollout"}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["governance"]["rollout"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{"Preparedness"}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["governance"]["preparedness"])}</ul></div>'
        "</div>"
        "</div>"
        '<div class="grid grid-cols-1 lg:grid-cols-2 gap-4" data-block="contracts">'
        '<div class="rounded-2xl border border-stone-200 p-4">'
        f'<div class="font-semibold mb-2">{input_contract_label}</div>'
        f'<div class="text-xs text-slate-500 mb-2">{"Потребитель" if language == "ru" else "Consumer"}: <span class="mono">{html.escape(agent["contracts"]["consumer"])}</span></div>'
        f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap">{render_code_block(agent["contracts"]["input_contract"])}</pre>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4">'
        f'<div class="font-semibold mb-2">{output_failure_label}</div>'
        f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap">{render_code_block(agent["contracts"]["output_contract"])}</pre>'
        f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap mt-3">{render_code_block(agent["contracts"]["failure_contract"])}</pre>'
        "</div>"
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="dependencies">'
        f'<div class="font-semibold mb-3">{"Зависимости" if language == "ru" else "Dependencies"}</div>'
        f'<div class="overflow-x-auto"><table class="w-full text-sm data-table"><thead><tr><th>{name_label}</th><th>{type_label}</th><th>{reason_label}</th><th>{risk_label}</th></tr></thead>'
        f"<tbody>{dependency_rows}</tbody></table></div>"
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="evaluation">'
        f'<div class="font-semibold mb-3">{"План eval" if language == "ru" else "Evaluation plan"}</div>'
        f'<div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm"><div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{scenarios_label}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["evaluation_plan"]["scenarios"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{metrics_label}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["evaluation_plan"]["metrics"])}</ul></div>'
        f'<div><div class="text-xs uppercase tracking-[0.14em] text-slate-400 mb-2">{regression_label}</div><ul class="list-disc pl-5 space-y-1">{html_list_items(agent["evaluation_plan"]["regression"])}</ul></div></div>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="delivery">'
        f'<div class="font-semibold mb-3">{"План внедрения" if language == "ru" else "Delivery plan"}</div>'
        f'<div class="grid grid-cols-1 xl:grid-cols-3 gap-4">{phases}</div>'
        f'<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4"><div class="subpanel"><div class="font-semibold mb-2">{observability_label}</div><ul class="list-disc pl-5 space-y-1 text-sm">{html_list_items(agent["delivery_plan"]["observability"])}</ul></div>'
        f'<div class="subpanel"><div class="font-semibold mb-2">{change_mgmt_label}</div><ul class="list-disc pl-5 space-y-1 text-sm">{html_list_items(agent["delivery_plan"]["change_management"])}</ul></div></div>'
        "</div>"
        "</article>"
    )


def render_design_dashboard(agents: list[dict], summary: dict, output_dir: Path) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    language = summary["language"]
    methodology = summary.get("methodology") or {}
    matrix_header, matrix_rows = derive_design_matrix(agents, language)
    contract_header, contract_rows = render_design_contract_matrix(summary)
    replacements = {
        "{{LANG}}": language,
        "{{PAGE_TITLE}}": html.escape(summary["title"]),
        "{{DASHBOARD_TITLE}}": html.escape(summary["title"]),
        "{{SUBTITLE}}": html.escape(summary["subtitle"]),
        "{{TAB_OVERVIEW}}": "Обзор" if language == "ru" else "Overview",
        "{{TAB_METHODOLOGY}}": "Методика" if language == "ru" else "Methodology",
        "{{TAB_AGENTS}}": "Units" if language == "ru" else "Units",
        "{{TAB_ISSUES}}": "Риски и delivery" if language == "ru" else "Risks and delivery",
        "{{OVERVIEW_SUMMARY_CARDS}}": render_overview_cards(summary),
        "{{ARCHITECTURE_HEADING}}": html.escape(summary["architecture"]["heading"]),
        "{{ARCHITECTURE_TEXT}}": html.escape(summary["architecture"]["text"]),
        "{{MERMAID_ARCHITECTURE}}": summary["architecture"]["mermaid"],
        "{{SCORES_HEADING}}": "Готовность к внедрению" if language == "ru" else "Implementation readiness",
        "{{METHODOLOGY_HEADING}}": html.escape(methodology.get("heading", "Методология design package" if language == "ru" else "Design package methodology")),
        "{{METHODOLOGY_LEAD}}": html.escape(methodology.get("lead", "Структурированный design package фиксирует boundary, governance и contracts до реализации." if language == "ru" else "The structured design package fixes boundary, governance, and contracts before implementation.")),
        "{{METHODOLOGY_LINKS}}": render_design_methodology_links(output_dir, language),
        "{{METHODOLOGY_SUMMARY_BLOCKS}}": render_design_methodology_blocks(summary),
        "{{AGENTS_LEAD}}": html.escape(summary["agents_lead"]),
        "{{AGENT_CARDS}}": (
            f'<div class="panel rounded-3xl p-5" data-block="agents-lead"><p class="text-sm text-slate-600">{html.escape(summary["agents_lead"])}</p></div>\n'
            + "\n".join(render_design_agent_card(agent, output_dir) for agent in agents)
        ),
        "{{CRITICAL_ISSUES_HEADING}}": "Критические риски" if language == "ru" else "Critical risks",
        "{{CRITICAL_ISSUES_ITEMS}}": render_design_critical_risks(summary),
        "{{MATURITY_MATRIX_HEADING}}": "Матрица внедрения" if language == "ru" else "Implementation matrix",
        "{{MATURITY_MATRIX_HEADER}}": matrix_header,
        "{{MATURITY_MATRIX_ROWS}}": matrix_rows,
        "{{CONTRACT_MATRIX_HEADING}}": "Матрица контрактов" if language == "ru" else "Contract matrix",
        "{{CONTRACT_MATRIX_TEXT}}": (
            "Строки показывают unit, столбцы — ключевые интерфейсы design package."
            if language == "ru"
            else "Rows show the unit, columns show the main interfaces defined by the design package."
        ),
        "{{CONTRACT_MATRIX_HEADER}}": contract_header,
        "{{CONTRACT_MATRIX_ROWS}}": contract_rows,
        "{{ROADMAP_HEADING}}": "Фазы внедрения" if language == "ru" else "Implementation phases",
        "{{ROADMAP_PHASES}}": render_design_roadmap(summary),
        "{{SCORE_ROWS}}": render_design_score_rows(agents),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", template)
    ensure(not unresolved, f"dashboard template still has unresolved placeholders: {sorted(set(unresolved))}")
    return template.rstrip() + "\n"


def render_design_package(input_dir: Path, output_dir: Path, *, check_only: bool) -> None:
    agents, summary = load_design_package(input_dir)
    agents = prepare_design_agents(agents)

    if check_only:
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        write_text(output_dir / f"{agent['metadata']['file_stem']}.md", render_design_markdown_agent(agent))
    write_text(output_dir / "README.md", render_design_markdown_summary(agents, summary))
    write_text(output_dir / "dashboard.html", render_design_dashboard(agents, summary, output_dir))


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()

    try:
        if args.kind == "review":
            render_review_package(input_dir, output_dir, check_only=args.check)
        else:
            render_design_package(input_dir, output_dir, check_only=args.check)
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.check:
        print(f"Structured {args.kind} package is valid.")
    else:
        print(f"Rendered {args.kind} package to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
