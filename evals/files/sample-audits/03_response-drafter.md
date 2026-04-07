# Аудит: агент `response-drafter`

## Источники

| Файл | Роль |
|---|---|
| `evals/files/sample-agents/agents/response-drafter.md` | исходный артефакт |
| `evals/files/sample-agents/src/tools/factory.py` | исходный артефакт |

## Вердикт

Итоговый балл: **16/30**

Response-drafter выделен как отдельная функция и не смешивается с поиском документов. Главная проблема сосредоточена в Control: prompt мотивирует сделать ответ полным даже на неполных данных. Для налогового сценария это делает agent unsafe-by-design.

## IDEF0

- **Input**: Агент принимает документы и подтверждённые факты от других агентов. Формат входа подразумевается, но не описан как schema.
- **Control**: Prompt требует написать полный ответ и заполнить пробелы из контекста. Ограничения на источники правды и честный refusal path отсутствуют.
- **Mechanism**: Toolkit `drafting` минимален и соответствует задаче форматирования ответа. Риск создаётся не инструментами, а policy prompt-а.
- **Output**: Выход — гибкий естественный текст без strict schema. Status для partial, empty и error path не определён.

## Критерии зрелости

| Критерий | Балл | Обоснование | Доказательства |
|---|---:|---|---|
| Граница функции | 2 | Функция финальной сборки ответа отделена от поиска и маршрутизации. | `evals/files/sample-agents/agents/response-drafter.md#L9-L10` |
| Input | 2 | Вход от других агентов понятен по роли, но не зафиксирован как structured handoff. | `evals/files/sample-agents/agents/response-drafter.md#L9-L12` |
| Control | 1 | Prompt описывает цель, но не ставит guardrails против выдумывания фактов. | `evals/files/sample-agents/agents/response-drafter.md#L11-L12` |
| Mechanism | 2 | Toolkit минимален и уместен для задачи финальной сборки ответа. | `evals/files/sample-agents/agents/response-drafter.md#L5-L7`, `evals/files/sample-agents/src/tools/factory.py#L1-L4` |
| Context engineering | 1 | Источник правды не отделён от вспомогательного контекста и это оставляет свободную зону для галлюцинации. | `evals/files/sample-agents/agents/response-drafter.md#L11-L12` |
| Runtime loop | 1 | Stop conditions и post-validation результата не описаны как runtime policy. | `evals/files/sample-agents/agents/response-drafter.md#L9-L12` |
| Evaluation | 2 | Fixture review существует, но негативные сценарии на incomplete input не выделены отдельно. | `evals/evals.json#L225-L239`, `evals/expected-findings.md#L13-L18` |
| Observability | 1 | Сигналов на refusal, partial output и hallucination detection в артефактах нет. | `evals/files/sample-agents/agents/response-drafter.md#L1-L12` |
| Safety | 1 | Prompt разрешает достраивать недостающие данные из контекста. | `evals/files/sample-agents/agents/response-drafter.md#L11` |
| Change management | 3 | Артефакты в версии есть и change risk на prompt хорошо локализуется по одному файлу. | `evals/files/sample-agents/agents/response-drafter.md#L1-L12`, `evals/review-dashboard-runbook.md#L112-L119` |

## Ключевые точки доказательства

- **Control** · `evals/files/sample-agents/agents/response-drafter.md#L11` · Prompt разрешает заполнять пробелы из контекста, а не только из подтверждённых фактов.
- **Output** · `evals/files/sample-agents/agents/response-drafter.md#L12` · Строгая схема результата не требуется и это делает downstream parsing хрупким.
- **Mechanism** · `evals/files/sample-agents/src/tools/factory.py#L3` · Toolkit сам по себе не создаёт риск, значит проблема локализована в Control.
- **Evaluation** · `evals/expected-findings.md#L13-L18` · Baseline review прямо ожидает finding про unsafe completion behavior.

## Контракты

Потребитель: `user + supervisor`

### Текущий

```text
Write a complete response. Keep the output flexible and natural, there is no need for a strict response schema.
```

### Целевой

```text
{
  "status": "success | partial | error",
  "draft": "string",
  "missing_inputs": ["string"],
  "reason": "string"
}
```

## Анти-паттерны

- **Unsafe completion**: Prompt провоцирует достраивание фактов вместо честной деградации.
- **Free-form output**: Результат нельзя надёжно валидировать программно.
- **Implicit input contract**: Supervisor не обязан передавать фиксированный набор подтверждённых фактов.

## Бэклог

| Приоритет | Слой | Риск | Действие | Файл |
|---|---|---|---|---|
| P1 | Control | Breaking | Запретить заполнение пробелов догадками и ввести honest partial path. | `evals/files/sample-agents/agents/response-drafter.md#L11-L12` |
| P1 | Output | Behavioural | Ввести strict response schema со status, draft и missing_inputs. | `evals/files/sample-agents/agents/response-drafter.md#L11-L12` |
| P2 | Input | Behavioural | Формализовать handoff от supervisor как список подтверждённых facts и documents. | `evals/files/sample-agents/agents/response-drafter.md#L9-L12` |

## План патчей

### 1. Запретить домысливание

- Точка: `evals/files/sample-agents/agents/response-drafter.md#L11`
- Тип патча: `prompt`
- Риск: `Breaking`

```text
If required facts are missing, do not fill gaps from context. Return status="partial" and list the missing inputs explicitly.
```

- [ ] Проверить incomplete-input сценарий и ожидать status=partial.
- [ ] Убедиться, что черновик не содержит неподтверждённых фактов.
- [ ] Проверить, что refusal/partial path стабилен в repeated runs.

### 2. Ввести строгий output contract

- Точка: `evals/files/sample-agents/agents/response-drafter.md#L11-L12`
- Тип патча: `schema`
- Риск: `Behavioural`

```text
{
  "status": "success | partial | error",
  "draft": "string",
  "missing_inputs": ["string"],
  "reason": "string"
}
```

- [ ] Проверить парсинг результата без regex-эвристик.
- [ ] Проверить success и partial paths.
- [ ] Проверить, что downstream consumer может валидировать schema.

### 3. Формализовать вход от supervisor

- Точка: `evals/files/sample-agents/agents/response-drafter.md#L9-L12`
- Тип патча: `schema`
- Риск: `Behavioural`

```text
Expected input: { "facts": [...], "documents": [...], "confidence": "string" }. Ignore any data outside this payload.
```

- [ ] Проверить, что agent использует только переданные поля.
- [ ] Проверить, что отсутствие facts приводит к partial path.
- [ ] Проверить cross-agent contract matrix после изменения.
