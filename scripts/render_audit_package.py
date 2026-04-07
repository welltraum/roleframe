#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = ROOT / "assets" / "dashboard-template.html"

CRITERIA_ORDER = [
    ("business_boundary", {"ru": "Граница функции", "en": "Business boundary"}),
    ("input_definition", {"ru": "Input", "en": "Input"}),
    ("control_layer", {"ru": "Control", "en": "Control"}),
    ("mechanism_layer", {"ru": "Mechanism", "en": "Mechanism"}),
    ("context_engineering", {"ru": "Context engineering", "en": "Context engineering"}),
    ("runtime_loop", {"ru": "Runtime loop", "en": "Runtime loop"}),
    ("evaluation", {"ru": "Evaluation", "en": "Evaluation"}),
    ("observability", {"ru": "Observability", "en": "Observability"}),
    ("safety", {"ru": "Safety", "en": "Safety"}),
    ("change_management", {"ru": "Change management", "en": "Change management"}),
]

SUMMARY_REQUIRED = {
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

AGENT_REQUIRED = {
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


class ValidationError(ValueError):
    """Raised when a structured audit package is incomplete."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a RoleFrame audit package from structured JSON.")
    parser.add_argument("--input", required=True, help="Directory with *.audit.json files or legacy audit markdown.")
    parser.add_argument("--output", required=True, help="Directory where markdown and dashboard views are written.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the package and exit without writing rendered files.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def sentence_count(text: str) -> int:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]
    return len(parts) if parts else 0


def level_from_score(score: int, language: str) -> str:
    labels = {
        "ru": [
            (10, "Эксперимент"),
            (20, "Рабочий прототип"),
            (25, "Управляемый агент"),
            (30, "Зрелый компонент"),
        ],
        "en": [
            (10, "Experiment"),
            (20, "Working prototype"),
            (25, "Managed agent"),
            (30, "Mature component"),
        ],
    }
    for threshold, label in labels.get(language, labels["en"]):
        if score <= threshold:
            return label
    return labels.get(language, labels["en"])[-1][1]


def criterion_labels(language: str) -> dict[str, str]:
    return {key: value.get(language, value["en"]) for key, value in CRITERIA_ORDER}


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_budget(name: str, text: str, *, min_sentences: int | None = None, max_sentences: int | None = None) -> None:
    count = sentence_count(text)
    if min_sentences is not None:
        ensure(count >= min_sentences, f"{name} must have at least {min_sentences} sentence(s)")
    if max_sentences is not None:
        ensure(count <= max_sentences, f"{name} must have at most {max_sentences} sentence(s)")


def validate_agent_audit(path: Path, payload: dict) -> None:
    missing = AGENT_REQUIRED - set(payload)
    ensure(not missing, f"{path.name} is missing keys: {sorted(missing)}")

    metadata = payload["metadata"]
    ensure(isinstance(metadata.get("name"), str) and metadata["name"], f"{path.name}: metadata.name is required")
    ensure(isinstance(metadata.get("language"), str) and metadata["language"], f"{path.name}: metadata.language is required")
    ensure(isinstance(metadata.get("source_files"), list) and metadata["source_files"], f"{path.name}: metadata.source_files must be a non-empty list")
    ensure(isinstance(metadata.get("reviewed_at"), str) and metadata["reviewed_at"], f"{path.name}: metadata.reviewed_at is required")

    summary = payload["summary"]
    ensure(isinstance(summary.get("total_score"), int), f"{path.name}: summary.total_score must be int")
    ensure(isinstance(summary.get("maturity_level"), str) and summary["maturity_level"], f"{path.name}: summary.maturity_level is required")
    ensure(isinstance(summary.get("verdict"), str) and summary["verdict"], f"{path.name}: summary.verdict is required")
    ensure(isinstance(summary.get("top_deficit"), str) and summary["top_deficit"], f"{path.name}: summary.top_deficit is required")
    validate_budget(f"{path.name}: summary.verdict", summary["verdict"], min_sentences=2, max_sentences=4)

    idef0 = payload["idef0"]
    for quadrant in ["input", "control", "mechanism", "output"]:
        ensure(isinstance(idef0.get(quadrant), str) and idef0[quadrant], f"{path.name}: idef0.{quadrant} is required")
        validate_budget(f"{path.name}: idef0.{quadrant}", idef0[quadrant], min_sentences=1, max_sentences=2)

    criteria = payload["criteria"]
    ensure(isinstance(criteria, list) and len(criteria) == 10, f"{path.name}: criteria must contain exactly 10 items")
    found_keys = {item.get("key") for item in criteria}
    expected_keys = {key for key, _ in CRITERIA_ORDER}
    ensure(found_keys == expected_keys, f"{path.name}: criteria keys must match the canonical 10 criteria")
    total_score = 0
    for item in criteria:
        ensure(isinstance(item.get("label"), str) and item["label"], f"{path.name}: each criterion needs label")
        ensure(isinstance(item.get("score"), int) and 0 <= item["score"] <= 3, f"{path.name}: criterion score must be 0..3")
        ensure(isinstance(item.get("rationale"), str) and item["rationale"], f"{path.name}: criterion rationale is required")
        ensure(isinstance(item.get("evidence"), list) and item["evidence"], f"{path.name}: criterion evidence must be a non-empty list")
        validate_budget(f"{path.name}: criterion {item['key']} rationale", item["rationale"], min_sentences=1, max_sentences=1)
        total_score += item["score"]
    ensure(total_score == summary["total_score"], f"{path.name}: summary.total_score must equal the sum of criteria")

    evidence_points = payload["evidence_points"]
    ensure(isinstance(evidence_points, list) and 3 <= len(evidence_points) <= 5, f"{path.name}: evidence_points must contain 3..5 items")
    for item in evidence_points:
        for field in ["layer", "source", "claim"]:
            ensure(isinstance(item.get(field), str) and item[field], f"{path.name}: evidence point {field} is required")

    contracts = payload["contracts"]
    for field in ["consumer", "current_contract", "target_contract"]:
        ensure(isinstance(contracts.get(field), str) and contracts[field], f"{path.name}: contracts.{field} is required")

    anti_patterns = payload["anti_patterns"]
    ensure(isinstance(anti_patterns, list) and 1 <= len(anti_patterns) <= 6, f"{path.name}: anti_patterns must contain 1..6 items")
    for item in anti_patterns:
        ensure(isinstance(item.get("tag"), str) and item["tag"], f"{path.name}: anti-pattern tag is required")
        ensure(isinstance(item.get("explanation"), str) and item["explanation"], f"{path.name}: anti-pattern explanation is required")

    backlog = payload["backlog"]
    ensure(isinstance(backlog, list) and 3 <= len(backlog) <= 6, f"{path.name}: backlog must contain 3..6 items")
    for item in backlog:
        for field in ["priority", "layer", "risk", "action", "file_ref"]:
            ensure(isinstance(item.get(field), str) and item[field], f"{path.name}: backlog {field} is required")

    patch_plan = payload["patch_plan"]
    ensure(isinstance(patch_plan, list) and len(patch_plan) == 3, f"{path.name}: patch_plan must contain exactly 3 items")
    for item in patch_plan:
        for field in ["title", "target", "patch_type", "risk", "draft"]:
            ensure(isinstance(item.get(field), str) and item[field], f"{path.name}: patch_plan {field} is required")
        ensure(isinstance(item.get("verification"), list) and item["verification"], f"{path.name}: patch_plan verification must be a non-empty list")


def validate_summary(path: Path, payload: dict, agents: list[dict]) -> None:
    missing = SUMMARY_REQUIRED - set(payload)
    ensure(not missing, f"{path.name} is missing keys: {sorted(missing)}")
    language = payload["language"]
    ensure(language in {"ru", "en"}, f"{path.name}: language must be ru or en")
    ensure(isinstance(payload["overview_cards"], list) and 3 <= len(payload["overview_cards"]) <= 4, f"{path.name}: overview_cards must contain 3..4 items")
    ensure(isinstance(payload["critical_issues"], list) and 3 <= len(payload["critical_issues"]) <= 5, f"{path.name}: critical_issues must contain 3..5 items")
    ensure(isinstance(payload["roadmap"], list) and len(payload["roadmap"]) >= 3, f"{path.name}: roadmap must contain at least 3 phases")
    canonical = payload["canonical_findings"]
    ensure(isinstance(canonical.get("matched"), int), f"{path.name}: canonical_findings.matched must be int")
    ensure(isinstance(canonical.get("total"), int) and canonical["total"] >= canonical["matched"], f"{path.name}: canonical_findings.total must be int >= matched")
    ensure(isinstance(canonical.get("categories"), list), f"{path.name}: canonical_findings.categories must be list")
    architecture = payload["architecture"]
    for field in ["heading", "text", "mermaid"]:
        ensure(isinstance(architecture.get(field), str) and architecture[field], f"{path.name}: architecture.{field} is required")
    maturity = payload["maturity_matrix"]
    ensure(isinstance(maturity.get("columns"), list) and maturity["columns"], f"{path.name}: maturity_matrix.columns must be non-empty")
    ensure(isinstance(maturity.get("rows"), list) and len(maturity["rows"]) == len(agents), f"{path.name}: maturity_matrix.rows must match agent count")
    contract = payload["contract_matrix"]
    ensure(isinstance(contract.get("columns"), list) and contract["columns"], f"{path.name}: contract_matrix.columns must be non-empty")
    ensure(isinstance(contract.get("rows"), list) and contract["rows"], f"{path.name}: contract_matrix.rows must be non-empty")
    methodology = payload.get("methodology", {})
    if methodology:
        ensure(isinstance(methodology.get("lead"), str) and methodology["lead"], f"{path.name}: methodology.lead is required when methodology block is present")
        ensure(isinstance(methodology.get("summary_blocks"), list) and methodology["summary_blocks"], f"{path.name}: methodology.summary_blocks must be non-empty")


def relative_href(output_dir: Path, target: str) -> str:
    target_path = (ROOT / target).resolve() if not Path(target).is_absolute() else Path(target)
    return Path(os.path.relpath(target_path, output_dir.resolve())).as_posix()


def render_code_block(value: str) -> str:
    return html.escape(value.strip())


def render_link_pill(output_dir: Path, target: str, label: str | None = None) -> str:
    href = relative_href(output_dir, target)
    text = html.escape(label or Path(target).name)
    return f'<a class="link-pill" href="{href}">{text}</a>'


def normalize_agent_order(agents: list[dict], language: str) -> list[dict]:
    labels = criterion_labels(language)
    key_order = {key: index for index, (key, _) in enumerate(CRITERIA_ORDER)}
    ordered: list[dict] = []
    for agent in agents:
        criteria_map = {item["key"]: item for item in agent["criteria"]}
        agent["criteria"] = [
            {
                **criteria_map[key],
                "label": criteria_map[key].get("label") or labels[key],
            }
            for key in key_order
        ]
        ordered.append(agent)
    return ordered


def import_legacy_agent(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    name_match = re.search(r"#\s+[^\n`]*`([^`]+)`", text)
    ensure(name_match is not None, f"{path.name}: cannot derive agent name from legacy markdown")
    score_match = re.search(r"(\d+)\s*/\s*30", text)
    ensure(score_match is not None, f"{path.name}: cannot derive total score from legacy markdown")
    verdict_match = re.search(r"##\s+Вердикт\s+.*?\*\*\d+/30\*\*\s+(.*?)\n##", text, re.S)
    ensure(verdict_match is not None, f"{path.name}: legacy markdown misses the expected verdict section")
    criteria_block = re.search(r"\| Критерий \| Балл \| Комментарий \|\n\|---\|---:\|---\|\n(.*?)\n##", text, re.S)
    ensure(criteria_block is not None, f"{path.name}: legacy markdown misses the criteria table")
    evidence_block = re.search(r"##\s+(Ключевые evidence points|Evidence)\b", text)
    contract_block = re.search(r"##\s+(Контракт ответа|Current vs target contract)\b", text)
    patch_block = re.search(r"##\s+(Patch plan|Patch plan, топ-3|Patch plan, top-3)\b", text)
    ensure(
        evidence_block and contract_block and patch_block,
        f"{path.name}: legacy markdown lacks structured sections for evidence/contracts/patch plan; rerun /roleframe review to produce *.audit.json",
    )

    raise ValidationError(
        f"{path.name}: legacy import is intentionally strict and only supports structured markdown generated by the JSON renderer; rerun /roleframe review to regenerate this package"
    )


def derive_summary(agents: list[dict], language: str) -> dict:
    total_score = sum(agent["summary"]["total_score"] for agent in agents)
    avg_score = round(total_score / len(agents), 1) if agents else 0.0
    worst = min(agents, key=lambda item: item["summary"]["total_score"]) if agents else None
    columns = ["agent", "boundary", "control", "mechanism", "eval", "safety", "total"]
    maturity_rows = []
    for agent in agents:
        criteria = {item["key"]: item for item in agent["criteria"]}
        maturity_rows.append(
            {
                "agent": agent["metadata"]["name"],
                "values": [
                    criteria["business_boundary"]["score"],
                    criteria["control_layer"]["score"],
                    criteria["mechanism_layer"]["score"],
                    criteria["evaluation"]["score"],
                    criteria["safety"]["score"],
                    agent["summary"]["total_score"],
                ],
            }
        )

    return {
        "language": language,
        "title": "Dashboard аудита агентов" if language == "ru" else "Agent audit dashboard",
        "subtitle": "Рендер из structured audit package" if language == "ru" else "Rendered from the structured audit package",
        "overall_verdict": (
            "Пакет показывает управляемую схему review: подробность теперь живёт в JSON и детерминированном рендере, а не в дублировании prose."
            if language == "ru"
            else "The package now uses a controlled review flow: detail lives in JSON and deterministic rendering instead of duplicated prose."
        ),
        "overview_cards": [
            {
                "title": "Общий вердикт" if language == "ru" else "Overall verdict",
                "value": level_from_score(round(avg_score), language),
                "description": (
                    "Дашборд собирается детерминированно из structured audit package."
                    if language == "ru"
                    else "The dashboard is rendered deterministically from the structured audit package."
                ),
            },
            {
                "title": "Средний балл" if language == "ru" else "Average score",
                "value": f"{avg_score}/30",
                "description": (
                    "Главные риски обычно приходятся на contracts, safety и eval."
                    if language == "ru"
                    else "The main risks typically cluster around contracts, safety, and evaluation."
                ),
            },
            {
                "title": "Агентов" if language == "ru" else "Agents",
                "value": str(len(agents)),
                "description": (
                    "Каждая карточка опирается на evidence, criteria, contracts и backlog."
                    if language == "ru"
                    else "Each card is backed by evidence, criteria, contracts, and backlog."
                ),
            },
            {
                "title": "Главный риск" if language == "ru" else "Top risk",
                "value": html.escape(worst["summary"]["top_deficit"]) if worst else "-",
                "description": (
                    "Самый слабый агент определяет системный приоритет исправлений."
                    if language == "ru"
                    else "The weakest agent defines the first system-level fix."
                ),
            },
        ],
        "canonical_findings": {
            "matched": 0,
            "total": 0,
            "categories": [],
        },
        "architecture": {
            "heading": "Архитектурная схема" if language == "ru" else "Architecture",
            "text": (
                "Схема построена по данным structured audit package и выделяет только самые рискованные связи."
                if language == "ru"
                else "The diagram is derived from the structured audit package and highlights only the riskiest links."
            ),
            "mermaid": "flowchart LR\n    A[\"Input\"] --> B[\"Agent review package\"] --> C[\"Dashboard\"]",
        },
        "critical_issues": [
            (
                f"{worst['metadata']['name']}: {worst['summary']['top_deficit']}"
                if worst
                else ("Нет данных" if language == "ru" else "No data")
            ),
            (
                "Следующим шагом нужно закрыть typed contracts и evidence completeness."
                if language == "ru"
                else "The next step is to close typed contracts and evidence completeness."
            ),
            (
                "Без structured output dashboard снова станет пересказом markdown."
                if language == "ru"
                else "Without structured output the dashboard becomes a markdown retelling again."
            ),
        ],
        "maturity_matrix": {
            "columns": columns,
            "rows": maturity_rows,
        },
        "contract_matrix": {
            "columns": [agent["metadata"]["name"] for agent in agents],
            "rows": [],
        },
        "roadmap": [
            {
                "title": "Фаза 1. Contracts" if language == "ru" else "Phase 1. Contracts",
                "description": (
                    "Закрыть typed output и handoff contracts."
                    if language == "ru"
                    else "Close typed output and handoff contracts."
                ),
            },
            {
                "title": "Фаза 2. Runtime и safety" if language == "ru" else "Phase 2. Runtime and safety",
                "description": (
                    "Формализовать retry, timeout, refusal и partial paths."
                    if language == "ru"
                    else "Formalize retry, timeout, refusal, and partial paths."
                ),
            },
            {
                "title": "Фаза 3. Eval и observability" if language == "ru" else "Phase 3. Eval and observability",
                "description": (
                    "Добавить agent-level regression и продуктовые сигналы."
                    if language == "ru"
                    else "Add agent-level regression and operational signals."
                ),
            },
        ],
        "agents_lead": (
            "Карточки ниже должны быть полезны без открытия markdown-файла: в них уже есть IDEF0, evidence, criteria, contracts и backlog."
            if language == "ru"
            else "The cards below should be useful without opening the markdown file: they already include IDEF0, evidence, criteria, contracts, and backlog."
        ),
    }


def load_package(input_dir: Path) -> tuple[list[dict], dict, bool]:
    audit_json_paths = sorted(input_dir.glob("[0-9][0-9]_*.audit.json"))
    summary_path = input_dir / "summary.audit.json"
    imported_legacy = False

    if audit_json_paths:
        agents = [read_json(path) for path in audit_json_paths]
        for path, payload in zip(audit_json_paths, agents):
            validate_agent_audit(path, payload)
        ensure(summary_path.exists(), f"{summary_path.name} is required when structured audit JSON files exist")
        summary = read_json(summary_path)
        validate_summary(summary_path, summary, agents)
        language = summary["language"]
        return normalize_agent_order(agents, language), summary, imported_legacy

    legacy_paths = sorted(path for path in input_dir.glob("[0-9][0-9]_*.md") if path.name != "README.md")
    ensure(legacy_paths, f"No structured audit JSON or legacy audit markdown files found in {input_dir}")
    agents = [import_legacy_agent(path) for path in legacy_paths]
    language = agents[0]["metadata"]["language"]
    summary = derive_summary(agents, language)
    imported_legacy = True
    return normalize_agent_order(agents, language), summary, imported_legacy


def html_list_items(items: list[str]) -> str:
    return "".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_markdown_agent(agent: dict) -> str:
    lines: list[str] = []
    language = agent["metadata"]["language"]
    source_label = "исходный артефакт" if language == "ru" else "source artifact"
    name = agent["metadata"]["name"]
    lines.append(f"# Аудит: агент `{name}`" if language == "ru" else f"# Audit: agent `{name}`")
    lines.append("")
    lines.append("## Источники" if language == "ru" else "## Sources")
    lines.append("")
    lines.append("| Файл | Роль |" if language == "ru" else "| File | Role |")
    lines.append("|---|---|")
    for source in agent["metadata"]["source_files"]:
        lines.append(f"| `{source}` | {source_label} |")
    lines.append("")
    lines.append("## Вердикт" if language == "ru" else "## Verdict")
    lines.append("")
    lines.append(f"Итоговый балл: **{agent['summary']['total_score']}/30**" if language == "ru" else f"Total score: **{agent['summary']['total_score']}/30**")
    lines.append("")
    lines.append(agent["summary"]["verdict"])
    lines.append("")
    lines.append("## IDEF0")
    lines.append("")
    for quadrant in ["input", "control", "mechanism", "output"]:
        lines.append(f"- **{quadrant.title()}**: {agent['idef0'][quadrant]}")
    lines.append("")
    lines.append("## Критерии зрелости" if language == "ru" else "## Maturity criteria")
    lines.append("")
    lines.append("| Критерий | Балл | Обоснование | Доказательства |" if language == "ru" else "| Criterion | Score | Rationale | Evidence |")
    lines.append("|---|---:|---|---|")
    for item in agent["criteria"]:
        evidence = ", ".join(f"`{entry}`" for entry in item["evidence"])
        lines.append(f"| {item['label']} | {item['score']} | {item['rationale']} | {evidence} |")
    lines.append("")
    lines.append("## Ключевые точки доказательства" if language == "ru" else "## Key evidence points")
    lines.append("")
    for item in agent["evidence_points"]:
        lines.append(f"- **{item['layer']}** · `{item['source']}` · {item['claim']}")
    lines.append("")
    lines.append("## Контракты" if language == "ru" else "## Contracts")
    lines.append("")
    lines.append(f"Потребитель: `{agent['contracts']['consumer']}`" if language == "ru" else f"Consumer: `{agent['contracts']['consumer']}`")
    lines.append("")
    lines.append("### Текущий" if language == "ru" else "### Current")
    lines.append("")
    lines.append("```text")
    lines.append(agent["contracts"]["current_contract"].strip())
    lines.append("```")
    lines.append("")
    lines.append("### Целевой" if language == "ru" else "### Target")
    lines.append("")
    lines.append("```text")
    lines.append(agent["contracts"]["target_contract"].strip())
    lines.append("```")
    lines.append("")
    lines.append("## Анти-паттерны" if language == "ru" else "## Anti-patterns")
    lines.append("")
    for item in agent["anti_patterns"]:
        lines.append(f"- **{item['tag']}**: {item['explanation']}")
    lines.append("")
    lines.append("## Бэклог" if language == "ru" else "## Backlog")
    lines.append("")
    lines.append("| Приоритет | Слой | Риск | Действие | Файл |" if language == "ru" else "| Priority | Layer | Risk | Action | File |")
    lines.append("|---|---|---|---|---|")
    for item in agent["backlog"]:
        lines.append(f"| {item['priority']} | {item['layer']} | {item['risk']} | {item['action']} | `{item['file_ref']}` |")
    lines.append("")
    lines.append("## План патчей" if language == "ru" else "## Patch plan")
    lines.append("")
    for index, item in enumerate(agent["patch_plan"], start=1):
        lines.append(f"### {index}. {item['title']}")
        lines.append("")
        lines.append(f"- Точка: `{item['target']}`" if language == "ru" else f"- Target: `{item['target']}`")
        lines.append(f"- Тип патча: `{item['patch_type']}`" if language == "ru" else f"- Patch type: `{item['patch_type']}`")
        lines.append(f"- Риск: `{item['risk']}`" if language == "ru" else f"- Risk: `{item['risk']}`")
        lines.append("")
        lines.append("```text")
        lines.append(item["draft"].strip())
        lines.append("```")
        lines.append("")
        lines.extend(f"- [ ] {entry}" for entry in item["verification"])
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def render_markdown_summary(agents: list[dict], summary: dict) -> str:
    language = summary["language"]
    lines = [
        "# Аудит агентов (методология RoleFrame)" if language == "ru" else "# Agent audit (RoleFrame methodology)",
        "",
        f"Основание: {summary['overall_verdict']}" if language == "ru" else f"Basis: {summary['overall_verdict']}",
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
            "| Агент | Балл | Уровень | Главный разрыв | Первое действие |"
            if language == "ru"
            else "| Agent | Score | Level | Main gap | First action |",
            "|---|---:|---|---|---|",
        ]
    )
    for agent in agents:
        lines.append(
            f"| `{agent['metadata']['name']}` | {agent['summary']['total_score']}/30 | {agent['summary']['maturity_level']} | {agent['summary']['top_deficit']} | {agent['patch_plan'][0]['title']} |"
        )
    lines.extend(
        [
            "",
            "## Межагентные находки" if language == "ru" else "## Cross-agent findings",
            "",
        ]
    )
    for item in summary["critical_issues"]:
        lines.append(f"- {item}")
    return "\n".join(lines).strip() + "\n"


def render_overview_cards(summary: dict) -> str:
    return "\n".join(
        [
            (
                '<div class="panel rounded-3xl p-5">'
                f'<div class="text-xs uppercase tracking-[0.18em] text-slate-400 mb-2">{html.escape(item["title"])}</div>'
                f'<div class="text-3xl font-extrabold">{html.escape(item["value"])}</div>'
                f'<div class="text-sm text-slate-500 mt-2">{html.escape(item["description"])}</div>'
                "</div>"
            )
            for item in summary["overview_cards"]
        ]
    )


def render_score_rows(agents: list[dict]) -> str:
    rows = []
    for agent in agents:
        score = agent["summary"]["total_score"]
        bar = min(100, round(score / 30 * 100))
        color = "bg-rose-500" if score <= 12 else ("bg-amber-500" if score <= 20 else "bg-emerald-600")
        rows.append(
            "<div>"
            f'<div class="flex justify-between text-sm mb-1"><span class="font-semibold">{html.escape(agent["metadata"]["name"])}</span><span>{score}/30, {html.escape(agent["summary"]["maturity_level"])}</span></div>'
            f'<div class="w-full h-3 bg-stone-200 rounded-full overflow-hidden"><div class="h-3 {color} score-bar" style="width:{bar}%"></div></div>'
            f'<div class="text-xs text-slate-500 mt-1">{html.escape(agent["summary"]["top_deficit"])}</div>'
            "</div>"
        )
    return "\n".join(rows)


def render_methodology_links(output_dir: Path, language: str) -> str:
    ru_label = "Открыть методологию, RU" if language == "ru" else "Open methodology, RU"
    en_label = "Открыть методологию, EN" if language == "ru" else "Open methodology, EN"
    summary_label = "Открыть сводку аудита" if language == "ru" else "Open audit summary"
    return "\n".join(
        [
            render_link_pill(output_dir, "docs/methodology.ru.md", ru_label),
            render_link_pill(output_dir, "docs/methodology.en.md", en_label),
            render_link_pill(output_dir, output_dir / "README.md", summary_label),
        ]
    )


def render_methodology_blocks(summary: dict) -> str:
    methodology = summary.get("methodology") or {}
    blocks = methodology.get("summary_blocks") or [
        {
            "title": "Что проверяется" if summary["language"] == "ru" else "What gets reviewed",
            "items": [
                "граница функции и typed contracts" if summary["language"] == "ru" else "function boundary and typed contracts",
                "разделение Control и Mechanism" if summary["language"] == "ru" else "control vs mechanism split",
                "наличие eval и observability" if summary["language"] == "ru" else "evaluation and observability coverage",
            ],
        },
        {
            "title": "Как читать пакет" if summary["language"] == "ru" else "How to read the package",
            "items": [
                "сначала overview, затем agent cards, затем markdown audit" if summary["language"] == "ru" else "start with the overview, then agent cards, then the markdown audit",
                "использовать dashboard для pattern-level анализа" if summary["language"] == "ru" else "use the dashboard for pattern-level analysis",
                "идти в markdown при подготовке patch plan" if summary["language"] == "ru" else "open markdown when preparing a patch plan",
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


def render_agent_card(agent: dict, output_dir: Path) -> str:
    language = agent["metadata"]["language"]
    badge_class = "badge-danger" if agent["summary"]["total_score"] <= 12 else "badge-warn"
    chip_class = "chip-danger" if any(item["priority"] == "P1" for item in agent["backlog"]) else "chip-warn"
    sources = [render_link_pill(output_dir, str(output_dir / f"{agent['metadata']['file_stem']}.md"), "Полный audit" if language == "ru" else "Full audit")]
    for source in agent["metadata"]["source_files"]:
        sources.append(render_link_pill(output_dir, source))
    evidence = "\n".join(
        [
            "<li>"
            f'<span class="mono">{html.escape(item["source"])}</span>, {html.escape(item["claim"])}'
            "</li>"
            for item in agent["evidence_points"]
        ]
    )
    criteria_rows = "\n".join(
        [
            "<tr>"
            f"<td>{html.escape(item['label'])}</td>"
            f"<td>{item['score']}</td>"
            f"<td>{html.escape(item['rationale'])}</td>"
            f"<td>{html.escape(', '.join(item['evidence']))}</td>"
            "</tr>"
            for item in agent["criteria"]
        ]
    )
    anti_patterns = "\n".join(
        [
            f'<span class="chip chip-neutral" title="{html.escape(item["explanation"])}">{html.escape(item["tag"])}</span>'
            for item in agent["anti_patterns"]
        ]
    )
    backlog_rows = "\n".join(
        [
            "<tr>"
            f"<td>{html.escape(item['action'])}</td>"
            f"<td>{html.escape(item['layer'])}</td>"
            f"<td><span class=\"chip {'chip-danger' if item['risk'].lower().startswith('break') else 'chip-warn' if item['risk'].lower().startswith('behav') else 'chip-good'}\">{html.escape(item['risk'])}</span></td>"
            f"<td><span class=\"mono\">{html.escape(item['file_ref'])}</span></td>"
            "</tr>"
            for item in agent["backlog"]
        ]
    )
    patch_cards = "\n".join(
        [
            '<div class="rounded-2xl border border-stone-200 p-4" data-block="patch-plan-item">'
            f'<div class="font-semibold mb-1">{html.escape(item["title"])}</div>'
            f'<div class="text-xs text-slate-500 mb-2"><span class="mono">{html.escape(item["target"])}</span> · {html.escape(item["patch_type"])} · {html.escape(item["risk"])}</div>'
            f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap">{render_code_block(item["draft"])}</pre>'
            f'<ul class="list-disc pl-5 mt-3 space-y-1 text-xs">{html_list_items(item["verification"])}</ul>'
            "</div>"
            for item in agent["patch_plan"]
        ]
    )

    return (
        f'<article class="panel rounded-3xl p-6 space-y-5" data-agent-card="{html.escape(agent["metadata"]["name"])}">'
        '<div class="flex flex-wrap items-center justify-between gap-3">'
        f'<div><h2 class="text-xl font-bold">{html.escape(agent["metadata"]["name"])}</h2>'
        f'<p class="text-sm text-slate-500">{html.escape(agent["summary"]["top_deficit"])}</p></div>'
        f'<div class="flex items-center gap-2"><span class="{badge_class} rounded-full px-3 py-1 text-sm font-bold">{agent["summary"]["total_score"]}/30</span>'
        f'<span class="chip {chip_class}">{html.escape(agent["summary"]["maturity_level"])}</span></div>'
        "</div>"
        f'<div class="flex flex-wrap gap-2" data-block="sources">{"".join(sources)}</div>'
        '<div class="rounded-2xl bg-stone-50 border border-stone-200 p-4" data-block="verdict">'
        f'<div class="font-semibold mb-2">{"Краткий вердикт" if language == "ru" else "Short verdict"}</div>'
        f'<p class="text-sm">{html.escape(agent["summary"]["verdict"])}</p>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="idef0">'
        f'<div class="font-semibold mb-3">IDEF0</div>'
        f'<div class="space-y-2 text-sm"><div><strong>Input:</strong> {html.escape(agent["idef0"]["input"])}</div>'
        f'<div><strong>Control:</strong> {html.escape(agent["idef0"]["control"])}</div>'
        f'<div><strong>Mechanism:</strong> {html.escape(agent["idef0"]["mechanism"])}</div>'
        f'<div><strong>Output:</strong> {html.escape(agent["idef0"]["output"])}</div></div>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="evidence">'
        f'<div class="font-semibold mb-3">{"Ключевые точки доказательства" if language == "ru" else "Key evidence points"}</div>'
        f'<ul class="list-disc pl-5 space-y-2 text-sm">{evidence}</ul>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="criteria">'
        f'<div class="font-semibold mb-3">{"Критерии зрелости" if language == "ru" else "Maturity criteria"}</div>'
        '<div class="overflow-x-auto"><table class="w-full text-sm data-table"><thead><tr>'
        f'<th>{"Критерий" if language == "ru" else "Criterion"}</th><th>{"Балл" if language == "ru" else "Score"}</th><th>{"Почему" if language == "ru" else "Why"}</th><th>{"Доказательства" if language == "ru" else "Evidence"}</th>'
        f"</tr></thead><tbody>{criteria_rows}</tbody></table></div>"
        "</div>"
        '<div class="grid grid-cols-1 lg:grid-cols-2 gap-4" data-block="contracts">'
        '<div class="rounded-2xl border border-stone-200 p-4">'
        f'<div class="font-semibold mb-2">{"Текущий контракт" if language == "ru" else "Current contract"}</div>'
        f'<div class="text-xs text-slate-500 mb-2">{"Потребитель" if language == "ru" else "Consumer"}: <span class="mono">{html.escape(agent["contracts"]["consumer"])}</span></div>'
        f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap">{render_code_block(agent["contracts"]["current_contract"])}</pre>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4">'
        f'<div class="font-semibold mb-2">{"Целевой контракт" if language == "ru" else "Target contract"}</div>'
        f'<pre class="mono text-xs bg-slate-900 text-slate-100 rounded-xl p-3 overflow-x-auto whitespace-pre-wrap">{render_code_block(agent["contracts"]["target_contract"])}</pre>'
        "</div>"
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="anti-patterns">'
        f'<div class="font-semibold mb-2">{"Анти-паттерны и системные риски" if language == "ru" else "Anti-patterns and systemic risks"}</div>'
        f'<div class="flex flex-wrap gap-2">{anti_patterns}</div>'
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="backlog">'
        f'<div class="font-semibold mb-3">{"Бэклог" if language == "ru" else "Backlog"}</div>'
        '<div class="overflow-x-auto"><table class="w-full text-sm data-table"><thead><tr>'
        f'<th>{"Действие" if language == "ru" else "Action"}</th><th>{"Слой" if language == "ru" else "Layer"}</th><th>{"Риск" if language == "ru" else "Risk"}</th><th>{"Точка" if language == "ru" else "File"}</th>'
        f"</tr></thead><tbody>{backlog_rows}</tbody></table></div>"
        "</div>"
        '<div class="rounded-2xl border border-stone-200 p-4" data-block="patch-plan">'
        f'<div class="font-semibold mb-3">{"План патчей, топ-3" if language == "ru" else "Patch plan, top-3"}</div>'
        f'<div class="grid grid-cols-1 xl:grid-cols-3 gap-4">{patch_cards}</div>'
        "</div>"
        "</article>"
    )


def render_critical_issues(summary: dict) -> str:
    return "\n".join(f"<p><strong>{index}.</strong> {html.escape(item)}</p>" for index, item in enumerate(summary["critical_issues"], start=1))


def render_maturity_matrix(summary: dict) -> tuple[str, str]:
    rows = []
    language = summary["language"]
    for row in summary["maturity_matrix"]["rows"]:
        values = "".join(f"<td>{html.escape(str(value))}</td>" for value in row["values"])
        rows.append(f"<tr><td><span class=\"mono\">{html.escape(row['agent'])}</span></td>{values}</tr>")
    columns = summary["maturity_matrix"]["columns"]
    header_labels = {
        "agent": "Агент" if language == "ru" else "Agent",
        "boundary": "Граница" if language == "ru" else "Boundary",
        "control": "Control",
        "mechanism": "Mechanism",
        "eval": "Eval",
        "safety": "Safety",
        "total": "Итог" if language == "ru" else "Total",
    }
    header = "".join(f"<th>{html.escape(header_labels.get(column, column.title()))}</th>" for column in columns)
    return header, "\n".join(rows)


def render_contract_matrix(summary: dict) -> tuple[str, str]:
    columns = summary["contract_matrix"]["columns"]
    header = "<th>Источник</th>" if summary["language"] == "ru" else "<th>Source</th>"
    header += "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    rows = []
    for row in summary["contract_matrix"]["rows"]:
        cells = "".join(
            f'<td><span class="chip chip-neutral">{html.escape(cell["status"])}</span><div class="text-xs text-slate-500 mt-1">{html.escape(cell["note"])}</div></td>'
            for cell in row["cells"]
        )
        rows.append(f"<tr><td><span class=\"mono\">{html.escape(row['agent'])}</span></td>{cells}</tr>")
    return header, "\n".join(rows)


def render_roadmap(summary: dict) -> str:
    return "\n".join(
        [
            '<div class="rounded-2xl border border-stone-200 p-4">'
            f'<div class="font-semibold">{html.escape(item["title"])}</div>'
            f'<p class="text-slate-600 mt-1">{html.escape(item["description"])}</p>'
            "</div>"
            for item in summary["roadmap"]
        ]
    )


def render_dashboard(agents: list[dict], summary: dict, output_dir: Path) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    language = summary["language"]
    methodology = summary.get("methodology") or {}
    maturity_header, maturity_rows = render_maturity_matrix(summary)
    contract_header, contract_rows = render_contract_matrix(summary)
    replacements = {
        "{{LANG}}": language,
        "{{PAGE_TITLE}}": html.escape(summary["title"]),
        "{{DASHBOARD_TITLE}}": html.escape(summary["title"]),
        "{{SUBTITLE}}": html.escape(summary["subtitle"]),
        "{{TAB_OVERVIEW}}": "Обзор" if language == "ru" else "Overview",
        "{{TAB_METHODOLOGY}}": "Методика" if language == "ru" else "Methodology",
        "{{TAB_AGENTS}}": "Агенты" if language == "ru" else "Agents",
        "{{TAB_ISSUES}}": "Проблемы и план" if language == "ru" else "Issues and roadmap",
        "{{OVERVIEW_SUMMARY_CARDS}}": render_overview_cards(summary),
        "{{ARCHITECTURE_HEADING}}": html.escape(summary["architecture"]["heading"]),
        "{{ARCHITECTURE_TEXT}}": html.escape(summary["architecture"]["text"]),
        "{{MERMAID_ARCHITECTURE}}": summary["architecture"]["mermaid"],
        "{{SCORES_HEADING}}": "Баллы зрелости" if language == "ru" else "Maturity scores",
        "{{METHODOLOGY_HEADING}}": html.escape(methodology.get("heading", "Методология" if language == "ru" else "Methodology")),
        "{{METHODOLOGY_LEAD}}": html.escape(methodology.get("lead", "Подробная методология вынесена в документы, а дашборд оставляет только краткую карту чтения." if language == "ru" else "Detailed methodology lives in companion documents; the dashboard keeps only a compact reading guide.")),
        "{{METHODOLOGY_LINKS}}": render_methodology_links(output_dir, language),
        "{{METHODOLOGY_SUMMARY_BLOCKS}}": render_methodology_blocks(summary),
        "{{AGENTS_LEAD}}": html.escape(summary["agents_lead"]),
        "{{AGENT_CARDS}}": (
            f'<div class="panel rounded-3xl p-5" data-block="agents-lead"><p class="text-sm text-slate-600">{html.escape(summary["agents_lead"])}</p></div>\n'
            + "\n".join(render_agent_card(agent, output_dir) for agent in agents)
        ),
        "{{CRITICAL_ISSUES_HEADING}}": "Критические проблемы" if language == "ru" else "Critical issues",
        "{{CRITICAL_ISSUES_ITEMS}}": render_critical_issues(summary),
        "{{MATURITY_MATRIX_HEADING}}": "Матрица зрелости" if language == "ru" else "Maturity matrix",
        "{{MATURITY_MATRIX_HEADER}}": maturity_header,
        "{{MATURITY_MATRIX_ROWS}}": maturity_rows,
        "{{CONTRACT_MATRIX_HEADING}}": "Матрица контрактов" if language == "ru" else "Contract matrix",
        "{{CONTRACT_MATRIX_TEXT}}": (
            "Строки показывают источник handoff, столбцы — потребителя. Каждая ячейка хранит статус и инженерный риск."
            if language == "ru"
            else "Rows show the handoff source, columns show the consumer. Each cell stores the status and the engineering risk."
        ),
        "{{CONTRACT_MATRIX_HEADER}}": contract_header,
        "{{CONTRACT_MATRIX_ROWS}}": contract_rows,
        "{{ROADMAP_HEADING}}": "Дорожная карта" if language == "ru" else "Roadmap",
        "{{ROADMAP_PHASES}}": render_roadmap(summary),
        "{{SCORE_ROWS}}": render_score_rows(agents),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    unresolved = re.findall(r"\{\{[A-Z0-9_]+\}\}", template)
    ensure(not unresolved, f"dashboard template still has unresolved placeholders: {sorted(set(unresolved))}")
    return template.rstrip() + "\n"


def prepare_agents_for_render(agents: list[dict]) -> list[dict]:
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


def render_package(input_dir: Path, output_dir: Path, *, check_only: bool) -> None:
    agents, summary, imported_legacy = load_package(input_dir)
    agents = prepare_agents_for_render(agents)
    if imported_legacy:
        raise ValidationError(
            "Legacy markdown import is available only as a compatibility probe. This package lacks the structured sections required for deterministic rendering; rerun /roleframe review to create *.audit.json files."
        )

    if check_only:
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    for agent in agents:
        write_text(output_dir / f"{agent['metadata']['file_stem']}.md", render_markdown_agent(agent))
    write_text(output_dir / "README.md", render_markdown_summary(agents, summary))
    write_text(output_dir / "dashboard.html", render_dashboard(agents, summary, output_dir))


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    try:
        render_package(input_dir, output_dir, check_only=args.check)
    except ValidationError as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.check:
        print("Structured audit package is valid.")
    else:
        print(f"Rendered audit package to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
