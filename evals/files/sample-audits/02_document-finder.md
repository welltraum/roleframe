# Аудит: агент `document-finder`

## Источники

| Файл | Роль |
|---|---|
| `evals/files/sample-agents/agents/document-finder.md` | исходный артефакт |
| `evals/files/sample-agents/src/tools/factory.py` | исходный артефакт |

## Вердикт

Итоговый балл: **18/30**

Document-finder уже близок к атомарной бизнес-функции. Главные пробелы сосредоточены не в назначении агента, а в handoff и failure policy. Пока результат годится для прототипа, но не для надёжного multi-agent контракта.

## IDEF0

- **Input**: Агент получает запрос на поиск документов от supervisor. Формат входа ожидается текстом, а не схемой.
- **Control**: Prompt требует найти релевантные документы и сообщить о пустом результате. Правила retry и handoff описаны эвристически.
- **Mechanism**: Toolkit `docs-search` даёт search и fetch capabilities. Runtime policy на timeout, retry count и budget не зафиксирована.
- **Output**: Агент возвращает лучшие документы или сообщение об отсутствии результата. Машинный payload со status и bounded result set не задан.

## Критерии зрелости

| Критерий | Балл | Обоснование | Доказательства |
|---|---:|---|---|
| Граница функции | 3 | Функция поиска документов выделена отдельно и читается однозначно. | `evals/files/sample-agents/agents/document-finder.md#L9-L11` |
| Input | 2 | Вход понятен по роли агента, но не оформлен как typed schema. | `evals/files/sample-agents/agents/document-finder.md#L9-L11` |
| Control | 2 | Happy path понятен, но contract для failure и handoff остаётся неполным. | `evals/files/sample-agents/agents/document-finder.md#L11-L14` |
| Mechanism | 2 | Toolkit соответствует назначению, но execution policy не доведена до runtime contract. | `evals/files/sample-agents/agents/document-finder.md#L5-L7`, `evals/files/sample-agents/src/tools/factory.py#L1-L4` |
| Context engineering | 1 | Правила сокращения выдачи и budget на payload не заданы. | `evals/files/sample-agents/agents/document-finder.md#L11-L14` |
| Runtime loop | 1 | Retry описан как эвристика и не содержит timeout или give-up policy. | `evals/files/sample-agents/agents/document-finder.md#L12` |
| Evaluation | 2 | Fixture review существует, но отдельные негативные сценарии агента не выделены. | `evals/evals.json#L225-L239`, `evals/expected-findings.md#L10-L14` |
| Observability | 1 | Signals для empty result и retry count не оформлены как operations artifacts. | `evals/files/sample-agents/agents/document-finder.md#L1-L14` |
| Safety | 2 | Агент не обещает лишнего, но tool-failure path всё ещё слаб. | `evals/files/sample-agents/agents/document-finder.md#L12-L14` |
| Change management | 2 | Версионность есть, но change cycle не закрыт негативными regression checks. | `evals/review-dashboard-runbook.md#L112-L119` |

## Ключевые точки доказательства

- **Control** · `evals/files/sample-agents/agents/document-finder.md#L11-L14` · Happy path описан, но handoff прямо разрешён без fixed schema.
- **Runtime** · `evals/files/sample-agents/agents/document-finder.md#L12` · Retry задан формулой “if it feels worth it”, а не проверяемой политикой.
- **Mechanism** · `evals/files/sample-agents/src/tools/factory.py#L1-L4` · Toolkit подтверждает, что у агента достаточно tools для функции поиска.
- **Contract** · `evals/files/sample-agents/agents/document-finder.md#L13-L14` · Empty result и success path существуют только как prose response supervisor-у.

## Контракты

Потребитель: `supervisor`

### Текущий

```text
Return the best documents in free text. If nothing is found, tell the supervisor that nothing is available.
```

### Целевой

```text
{
  "status": "success | empty | error",
  "documents": [{"id": "string", "title": "string", "relevance": 0.0}],
  "reason": "string"
}
```

## Анти-паттерны

- **Untyped handoff**: Supervisor не получает machine-readable payload.
- **Weak failure policy**: Timeout, retry count и give-up rules отсутствуют.
- **Budget risk**: Размер возвращаемого набора документов никак не ограничен.

## Бэклог

| Приоритет | Слой | Риск | Действие | Файл |
|---|---|---|---|---|
| P1 | Control | Behavioural | Ввести typed handoff payload со status, documents и reason. | `evals/files/sample-agents/agents/document-finder.md#L11-L14` |
| P1 | Runtime | Safe | Формализовать retry, timeout и give-up policy. | `evals/files/sample-agents/agents/document-finder.md#L12` |
| P2 | Context | Safe | Ограничить размер payload и число возвращаемых документов. | `evals/files/sample-agents/agents/document-finder.md#L11-L14` |

## План патчей

### 1. Typed handoff для найденных документов

- Точка: `evals/files/sample-agents/agents/document-finder.md#L11-L14`
- Тип патча: `schema`
- Риск: `Behavioural`

```text
{
  "status": "success | empty | error",
  "documents": [{"id": "string", "title": "string", "relevance": 0.0}],
  "reason": "string"
}
```

- [ ] Проверить happy path с 1-3 документами.
- [ ] Проверить empty path без найденных документов.
- [ ] Проверить, что supervisor может разобрать payload без эвристики.

### 2. Failure policy вместо эвристического retry

- Точка: `evals/files/sample-agents/agents/document-finder.md#L12`
- Тип патча: `runtime`
- Риск: `Safe`

```text
If the tool fails, retry once. If the second attempt fails or times out, return status="error" and include the failure reason.
```

- [ ] Смоделировать timeout и убедиться, что агент возвращает status=error.
- [ ] Проверить, что число retry не превышает один.
- [ ] Проверить, что текст prompt больше не использует эвристику feel-worth-it.

### 3. Budget rule для результата поиска

- Точка: `evals/files/sample-agents/agents/document-finder.md#L11-L14`
- Тип патча: `prompt`
- Риск: `Safe`

```text
Return at most 3 documents. Pass ids, titles, and short evidence snippets instead of full document bodies.
```

- [ ] Проверить, что handoff не разрастается при большом количестве совпадений.
- [ ] Проверить, что relevance и ids сохраняются.
- [ ] Проверить, что response-drafter получает достаточно данных без context stuffing.
