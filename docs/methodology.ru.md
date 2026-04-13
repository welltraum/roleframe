# Методология governance unit

Документ опирается на `Инженерию агентов 2026`. Это короткая опора для чтения RoleFrame dashboard и structured package после перехода от agent-only модели к governance unit.

## 1. Governance unit, это не просто prompt

LLM не равна системе. Governance unit начинается там, где вокруг модели появились:

- ограничения и SOP
- tools и adapters
- manifests и ownership markers
- output contract
- eval и observability
- rollout и preparedness signals

Без этого перед нами prompt-прототип, а не управляемый unit.

## 2. Три профиля

RoleFrame использует один метод, но теперь поддерживает три профиля:

- `agent`, одна бизнес-функция
- `pack`, одна owner boundary с явными routes и proof surfaces
- `workflow`, один orchestration contour, который надо декомпозировать до аудита

Правила профилей:

- `agent`: не принимать brief формата “делает всё”
- `pack`: не допускать parallel owner surfaces
- `workflow`: сначала карта контура, потом split на units

## 3. IDEF0 не меняется

IDEF0 остаётся каркасом требований.

### Input

Что входит в unit:

- запрос
- событие
- файл
- handoff
- route payload

### Control

Что управляет unit:

- role
- SOP
- constraints
- contract
- decision rules

Prompt и policy-файлы живут именно здесь.

### Mechanism

Чем unit исполняется:

- tools
- runtime
- manifests
- routes
- memory
- adapters
- rollout helpers

### Output

Что считается завершением:

- success
- business-empty
- technical failure
- partial / refusal
- delegation
- rollout или visibility signal

## 4. Минимальное правило проектирования теперь profile-aware

Один и тот же вопрос задаётся в трёх формах:

- `agent`: какая здесь одна бизнес-функция?
- `pack`: какая здесь одна owner boundary?
- `workflow`: что надо декомпозировать, чтобы граница стала честной?

Если это нельзя выразить одним предложением, текущий unit слишком широк.

## 5. Приоритет доказательств в review

Доверяй артефактам в таком порядке:

1. runtime, manifests, adapters, tests, proof surfaces
2. prompts и policy-файлы
3. prose docs

Если prompt говорит одно, а route, test или manifest доказывает другое, доверяй исполнимому или proof-слою.

## 6. Что считается хорошим Control

Control должен фиксировать:

- identity
- узкую ответственность
- упорядоченный SOP
- ограничения
- typed output contract

Для `pack` сюда же входят route discipline и ownership rules. Для `workflow`, правила decomposition и escalation.

## 7. Что считается хорошим Mechanism

Mechanism должен делать контракт реальным:

- tools и права заданы явно
- routes типизированы
- retry и timeout ограничены
- owned surfaces и visible surfaces не конфликтуют
- tests и proof surfaces подтверждают рискованные утверждения

## 8. Что должно покрывать eval

Eval должен включать:

- happy path
- edge cases
- business-empty
- failure paths
- partial или refusal
- ошибки маршрутизации
- ownership conflicts
- drift proof surfaces

## 9. Практический минимум

Перед реализацией или rollout у governance unit должны быть:

1. зафиксированный профиль
2. ясное boundary statement
3. IDEF0 card
4. typed contracts
5. governance-данные: owner boundary, routes, owned surfaces, proof surfaces
6. eval-сценарии
7. rollout и observability signals

Если этих артефактов нет, команда всё ещё тюнит поведение “на ощущениях”.
