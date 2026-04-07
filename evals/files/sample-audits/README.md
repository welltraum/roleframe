# Аудит агентов (методология RoleFrame)

Основание: Fixture хорошо подходит для демонстрации evidence-driven review, но основная архитектурная слабость остаётся прежней: handoff и output живут как prose-контракты. JSON-first пакет убирает дублирование и позволяет делать плотный dashboard без повторного пересказа markdown.

## Файлы

- `01_supervisor.md`
- `02_document-finder.md`
- `03_response-drafter.md`

## Сводка

| Агент | Балл | Уровень | Главный разрыв | Первое действие |
|---|---:|---|---|---|
| `supervisor` | 12/30 | Рабочий прототип | Смешивает routing и final answer без typed contracts. | Ввести строгий выходной контракт |
| `document-finder` | 18/30 | Рабочий прототип | Нет typed handoff и формальной failure policy. | Typed handoff для найденных документов |
| `response-drafter` | 16/30 | Рабочий прототип | Prompt поощряет домысливание и не даёт честного partial path. | Запретить домысливание |

## Межагентные находки

- Supervisor смешивает routing и final answer, поэтому граница функции ломается первой.
- Document-finder не имеет typed handoff и детерминированной failure policy.
- Response-drafter unsafe-by-design, потому что prompt разрешает достраивать факты.
- Eval и observability существуют только на уровне fixture review, а не как per-agent contracts.
