# Шаблон рендера markdown-аудита

Используй этот layout как целевой markdown для `docs/roleframe/review/NN_name.md`.

Канонический источник истины: `docs/roleframe/review/NN_name.audit.json`.

Markdown остаётся derived view того же review package и не должен добавлять новые факты.

## Что должно попасть в markdown

| Раздел markdown | JSON-поле |
|---|---|
| Источники | `metadata.source_files` |
| Краткий вердикт | `summary.*` |
| Профиль | `metadata.unit_kind` |
| Карта артефактов | `artifact_inventory[]` |
| IDEF0 | `idef0.*` |
| Governance | `governance.*` |
| Критерии зрелости | `criteria[]` |
| Точки доказательства | `evidence_points[]` |
| Контракты | `contracts.*` |
| Anti-patterns | `anti_patterns[]` |
| Бэклог | `backlog[]` |
| Patch plan | `patch_plan[]` |

Подробная структура и budgets описаны в [structured-audit.md](structured-audit.md).

## Правила рендера

1. Весь markdown на языке запроса.
2. Каждый вывод должен быть проверяемым и опираться на артефакт или фиксированное отсутствие артефакта.
3. Сначала показывай inventory и governance, потом scoring и patch plan.
4. Не превращай dashboard в источник истины. Markdown и HTML лишь отображают один и тот же JSON.
5. Prompt archaeology допустима только как частный случай `agent`-profile review.
6. Для `pack` и `workflow` приоритет выше у manifest, route, runtime, tests, rollout helpers и proof surfaces.

## Форматы доказательств

Используй один из трёх типов:

### Прямая цитата

```text
Артефакт: [Control / Mechanism / Evaluation / Operations / Change management]
Источник: `path/to/file#L10-L18`
Тип: [prompt / manifest / route / runtime / test / proof_surface / doc]
Вывод: [что доказывает фрагмент]
```

### Структурный индикатор

```text
Артефакт: [слой]
Источник: `path/to/file#L...`
Тип: [schema / config / code]
Вывод: [какой инженерный вывод следует из структуры]
```

### Отсутствие артефакта

```text
Артефакт: [слой]
Проверено: [список файлов или директорий]
Не найдено: [чего именно нет]
Вывод: [какой риск из этого следует]
```

## Целевой layout

````markdown
# Аудит: unit `[имя]`

## Источники

| Файл | Роль файла | Что доказал в review |
|---|---|---|
| `...` | prompt / manifest / route / runtime / test / proof surface / doc | ... |

## Краткий вердикт

[2-4 предложения из `summary.verdict`]

## Профиль

`agent | pack | workflow`

## Карта артефактов

| Тип | Файл | Роль |
|---|---|---|
| `prompt` | `...` | ... |
| `manifest` | `...` | ... |
| `route` | `...` | ... |

## IDEF0

| Компонент | Что найдено |
|---|---|
| Input | ... |
| Control | ... |
| Mechanism | ... |
| Output | ... |

## Governance

- **Owner boundary**: ...

### Route matrix

| Source | Target | Status | Note |
|---|---|---|---|
| `...` | `...` | implicit / typed / absent | ... |

### Proof surfaces

- ...

### Deployment visibility

- ...

### Rollout

- ...

### Preparedness

- ...

## Критерии зрелости

| Критерий | Балл | Обоснование | Доказательства |
|---|---:|---|---|
| Boundary | 2 | ... | `file#Lx-Ly` |

## Ключевые точки доказательства

- **Control** · `path#L...` · ...
- **Mechanism** · `path#L...` · ...

## Контракты

Потребитель: `...`

### Текущий

```text
...
```

### Целевой

```text
...
```

## Anti-patterns

- **AP-...**: ...

## Бэклог

| Приоритет | Слой | Риск | Действие | Файл |
|---|---|---|---|---|
| P1 | Control | Breaking | ... | `path#L...` |

## План патчей

### 1. [Название]

- Точка: `...`
- Тип патча: `prompt | schema | route | runtime | test`
- Риск: `Breaking | Behavioural | Safe`

```text
[черновик изменения]
```

- [ ] [проверка 1]
- [ ] [проверка 2]
````

## Пояснения по профилям

- `agent`: inventory обычно начинается с prompt/policy, runtime и tool wiring, но всегда перепроверяется по runtime.
- `pack`: inventory начинается с manifest, routes, tests, rollout helpers и proof surfaces; prompt сам по себе не считается полным контрактом.
- `workflow`: сначала фиксируй decomposition и cross-unit contract matrix, затем оценивай каждый child unit.

## Что нельзя делать

- Не дублируй факты между markdown и JSON с разными формулировками.
- Не описывай dashboard как canonical truth.
- Не своди весь review к prose-анализу prompt, если есть runtime, manifests или proof surfaces.
- Не смешивай owner boundary, visibility и deployment в один общий абзац без route matrix.
