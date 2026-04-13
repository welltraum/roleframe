# Аудит: unit `supervisor`

## Источники

| Файл | Роль |
|---|---|
| `evals/files/sample-agents/agents/supervisor.md` | исходный артефакт |
| `evals/files/sample-agents/prompts/agents/supervisor.txt` | исходный артефакт |
| `evals/files/sample-agents/src/tools/factory.py` | исходный артефакт |

## Профиль

`profile: agent`

## Вердикт

Итоговый балл: **12/30**

Supervisor держит на себе маршрутизацию и финальную сборку ответа. Из-за этого граница функции размыта и contracts не читаются как инженерный интерфейс. Главный риск возникает в связке free-form output, hidden dependency и implicit handoff.

## Карта артефактов

| Тип | Файл | Роль |
|---|---|---|
| `prompt` | `evals/files/sample-agents/prompts/agents/supervisor.txt` | Control-слой с route logic и output policy. |
| `runtime` | `evals/files/sample-agents/agents/supervisor.md` | Passport и orchestration metadata. |
| `runtime` | `evals/files/sample-agents/src/tools/factory.py` | Подтверждает реальный toolkit. |
| `doc` | `evals/expected-findings.md` | Фиксирует baseline findings для fixture review. |

## IDEF0

- **Input**: Агент принимает запрос пользователя по налоговой теме и различает кейсы с документами и без них. Тип входа не описан как схема.
- **Control**: Prompt задаёт последовательность классификации, делегирования и финальной сборки ответа. Ограничения на честную деградацию и формат выхода не формализованы.
- **Mechanism**: Во frontmatter объявлены toolkit `docs-search`, два sub-agent и retry middleware. Реальный toolset берётся из factory и не совпадает с текстом prompt.
- **Output**: Выход описан как полезный свободный текст. Машинный success, empty, error и delegation contract отсутствуют.

## Governance

- **Owner boundary**: Supervisor должен владеть только route decision и typed handoff. Сейчас owner boundary размыта из-за финальной сборки ответа.

### Route matrix

| Source | Target | Status | Note |
|---|---|---|---|
| `supervisor` | `document-finder` | implicit | Handoff существует только как prose-описание. |
| `supervisor` | `response-drafter` | implicit | Route decision есть, но payload не типизирован. |
| `supervisor` | `user` | implicit | Final output уходит free text без strict schema. |

### Proof surfaces

- fixture review baseline в evals/expected-findings.md

### Deployment visibility

- deployed in fixture metadata
- visibility правил для route decision нет

### Rollout

- нет отдельного rollout gate для typed handoff

### Preparedness

- unit не готов к безопасному reuse без typed contracts

## Критерии зрелости

| Критерий | Балл | Обоснование | Доказательства |
|---|---:|---|---|
| Граница функции | 1 | Граница слишком широкая и объединяет orchestration с final answer. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L3-L9` |
| Input | 1 | Классы входов угадываются по тексту, но не описаны как contract. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L3-L5` |
| Control | 1 | Role и кусок SOP есть, но выходной контракт отсутствует. | `evals/files/sample-agents/agents/supervisor.md#L14-L16`, `evals/files/sample-agents/prompts/agents/supervisor.txt#L8-L9` |
| Mechanism | 1 | Prompt ссылается на tool, которого нет в объявленном toolkit. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L6`, `evals/files/sample-agents/src/tools/factory.py#L1-L4` |
| Context engineering | 1 | Правила загрузки и сокращения контекста в prompt не зафиксированы. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L1-L9` |
| Runtime loop | 1 | Retry указан в metadata, но лимиты шагов и stop conditions не описаны. | `evals/files/sample-agents/agents/supervisor.md#L11-L13` |
| Evaluation | 2 | Review fixture существует, но unit-level сценарии остаются частичными. | `evals/evals.json#L225-L239`, `evals/expected-findings.md#L7-L18` |
| Observability | 1 | Следов маршрутизации и отказов в fixture нет как отдельных артефактов. | `evals/files/sample-agents/agents/supervisor.md#L1-L16` |
| Safety | 1 | Prompt поощряет сглаживание пробелов вместо честного partial path. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L8-L9` |
| Change management | 2 | Артефакты в git есть, но регрессионный цикл для prompt и routing не описан. | `evals/review-dashboard-runbook.md#L112-L119` |

## Ключевые точки доказательства

- **Control** · `evals/files/sample-agents/prompts/agents/supervisor.txt#L3-L5` · Routing contract существует только как prose-правило без typed payload.
- **Mechanism** · `evals/files/sample-agents/prompts/agents/supervisor.txt#L6` · Prompt разрешает `archive_search`, которого нет в declared toolkit.
- **Mechanism** · `evals/files/sample-agents/src/tools/factory.py#L1-L4` · Factory подтверждает, что `docs-search` содержит только `search_documents` и `fetch_document`.
- **Safety** · `evals/files/sample-agents/prompts/agents/supervisor.txt#L8-L9` · Финальный ответ разрешён в free text и допускает заполнение пробелов.

## Контракты

Потребитель: `user + downstream review/dashboard tooling`

### Текущий

```text
Return a useful answer in free text.
```

### Целевой

```text
{
  "status": "success | empty | error | delegation",
  "selected_agent": "document-finder | response-drafter | null",
  "payload": {},
  "reason": "string"
}
```

## Анти-паттерны

- **AP-14 Hidden dependency**: Prompt требует capability вне declared toolkit.
- **Implicit routing contract**: Handoff между units не описан машинно.
- **Free-form output**: Итоговый ответ не имеет strict schema.
- **Safety risk**: Prompt разрешает сглаживание недостающих данных.

## Бэклог

| Приоритет | Слой | Риск | Действие | Файл |
|---|---|---|---|---|
| P1 | Control | Breaking | Ввести typed output contract для success / empty / error / delegation. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L8-L9` |
| P1 | Mechanism | Behavioural | Убрать `archive_search` из prompt или объявить capability в toolkit и factory. | `evals/files/sample-agents/prompts/agents/supervisor.txt#L6` |
| P1 | Architecture | Breaking | Разделить routing и final response по разным функциям или жёстко типизировать handoff. | `evals/files/sample-agents/agents/supervisor.md#L2-L16` |
| P2 | Runtime | Safe | Добавить step limit, honest stop policy и telemetry по выбранному маршруту. | `evals/files/sample-agents/agents/supervisor.md#L11-L13` |

## План патчей

### 1. Ввести строгий выходной контракт

- Точка: `evals/files/sample-agents/prompts/agents/supervisor.txt#L8-L9`
- Тип патча: `schema`
- Риск: `Breaking`

```text
{
  "status": "success | empty | error | delegation",
  "selected_agent": "document-finder | response-drafter | null",
  "payload": {},
  "reason": "string"
}
```

- [ ] Смоделировать happy-path с каждым downstream unit.
- [ ] Проверить empty и tool-error пути.
- [ ] Убедиться, что выход можно разобрать без эвристик.

### 2. Убрать скрытую зависимость

- Точка: `evals/files/sample-agents/prompts/agents/supervisor.txt#L6`
- Тип патча: `prompt`
- Риск: `Behavioural`

```text
Use only the tools declared in the assigned toolkit. If a required capability is missing, return status="error" with the missing capability name.
```

- [ ] Проверить, что prompt больше не упоминает `archive_search`.
- [ ] Сверить prompt c `src/tools/factory.py`.
- [ ] Убедиться, что review больше не ловит hidden dependency.

### 3. Сузить границу функции supervisor

- Точка: `evals/files/sample-agents/agents/supervisor.md#L2-L16`
- Тип патча: `prompt`
- Риск: `Breaking`

```text
Your only job is to classify the request and delegate it with a typed payload. Do not compose the final answer yourself.
```

- [ ] Проверить, что final answer остаётся только у response-drafter.
- [ ] Проверить, что supervisor возвращает route decision, а не prose response.
- [ ] Обновить contract matrix и негативные eval-кейсы.
