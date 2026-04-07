# Аудит: агент `supervisor`

## Вердикт

Итоговый балл: **12/30**

Supervisor держит на себе маршрутизацию и финальную сборку ответа, но граница функции размыта. В prompt одновременно живут routing-логика, обращение к неописанному tool и свободный текстовый output без typed contract.

## Критерии зрелости

| Критерий | Балл | Комментарий |
|---|---:|---|
| Граница функции | 1 | Агент описан слишком широко |
| Input | 1 | Классы входов не формализованы |
| Control | 1 | SOP есть частично, output contract отсутствует |
| Mechanism | 1 | Указан toolkit, но prompt ссылается на чужой tool |
| Context engineering | 1 | Нет правил загрузки контекста |
| Runtime loop | 1 | Retry есть в metadata, но лимиты шагов не описаны |
| Evaluation | 2 | Есть fixture для review |
| Observability | 1 | Сигналы не определены |
| Safety | 1 | Агент склонен "додумывать" недостающие данные |
| Change management | 2 | Артефакты в git, но регрессии не описаны |

## Топ-дефициты

1. Нет output contract для happy / empty / failure.
2. Prompt ссылается на `archive_search`, которого нет в toolkit.
3. Граница функции смешивает маршрутизацию и финальный ответ.

## Бэклог

| Приоритет | Риск | Действие | Точка |
|---|---|---|---|
| P1 | Breaking | Ввести typed output contract | `agents/supervisor.md#L1-L12` |
| P1 | Behavioural | Убрать скрытую зависимость `archive_search` | `prompts/agents/supervisor.txt#L3-L3` |
| P2 | Safe | Формализовать routing contract | `agents/supervisor.md#L1-L12` |
