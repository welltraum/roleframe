# Design: unit `catalog-query-designer`

## Verdict

Readiness: **74/100**, Implementation-ready draft

The design has a clear business boundary and typed contracts. The main remaining risk is incomplete instrumentation for retrieval quality and fallback quality.

## Profile

`profile: agent`

## Boundary

- **Goal**: Transform a fuzzy user request into a validated structured query for the product catalog API.
- **Consumer**: Catalog backend and search UI.

### Success criteria

- Returns a typed query object for supported intents.
- Explains business-empty outcomes without inventing unavailable filters.
- Produces a degraded contract when retrieval tools are unavailable.

### In scope

- Normalize user intent into catalog filters.
- Validate supported filter combinations.
- Return structured metadata for downstream search execution.

### Out of scope

- Executing checkout or order management flows.
- Recommending products without catalog evidence.
- Editing catalog data.

## IDEF0

- **Input**: User request text, locale, and optional dialog context enter the function. Unsupported intents are rejected before query assembly.
- **Control**: The prompt fixes the role, normalization SOP, unsupported-intent policy, and the output contract for success, empty, and degraded paths.
- **Mechanism**: The agent uses a catalog schema reference, validation rules, and retrieval tools. Runtime limits bound the number of tool calls and retries.
- **Output**: The function returns a typed structured query, a business-empty result, or a degraded response with retry guidance.

## Control

- **Role**: Catalog query planner for product search.

### SOP

1. Classify the request into a supported catalog intent.
2. Extract candidate entities, filters, and ambiguities.
3. Validate the filter set against the catalog schema.
4. Return the strict output contract with confidence and rationale.

### Constraints

- Do not invent unsupported filters or product facts.
- Do not return free-form prose as the primary payload.
- If the schema or tools are unavailable, return the degraded contract.

## Mechanism

| Tool | Purpose | Failure mode |
|---|---|---|
| `catalog_schema_lookup` | Resolve supported filter names and allowed values. | Return degraded output and request retry. |
| `catalog_examples_store` | Ground normalization on known query examples. | Continue without examples and lower confidence. |

- **Memory strategy**: Keep only the current request, active ambiguity notes, and the latest validated schema slice.
- **Runtime loop**: At most two lookup steps before producing the final contract. No recursive delegation.
- **Error handling**: Timeouts convert to degraded output. Validation mismatches return business-empty with clarification suggestions.

## Governance

- **Owner boundary**: Owns normalization from fuzzy request to typed catalog query. Does not own downstream search execution or catalog mutation.

### Routes

| Route | Consumer | Contract | Risk |
|---|---|---|---|
| `catalog-search-handoff` | `catalog-search-api` | { status, query, confidence, reasoning } | Parser drift in the downstream consumer. |

### Owned surfaces

- prompt policy for query normalization
- typed query contract

### Proof surfaces

- scenario regression for supported and unsupported intents
- timeout mock for degraded output

### Deployment visibility

- deployed internally behind the search UI
- not visible as a standalone end-user surface

### Rollout

- ship behind feature flag
- expand only after degraded-path monitoring is stable

### Preparedness

- typed contracts frozen with the UI consumer
- schema-drift alerts connected to release gates

## Contracts

Consumer: `catalog-search-api`

### Input

```text
{ request_text: string, locale: string, session_filters?: object }
```

### Output

```text
{ status: "success", query: object, confidence: number, reasoning: string[] } | { status: "empty", reason: string, suggestions: string[] }
```

### Failure

```text
{ status: "degraded", reason: string, retryable: boolean, fallback_action: string }
```

## Dependencies

| Name | Type | Reason | Risk |
|---|---|---|---|
| catalog schema service | API | Supplies the allowed filter vocabulary. | Schema drift breaks generated queries. |
| search UI | consumer | Consumes the typed payload and explanation metadata. | UI parser mismatch breaks the success path. |

## Evaluation plan

### Scenarios

- Happy path for brand + category + price filter queries.
- Unsupported intent that should be rejected cleanly.
- Tool timeout that must produce degraded output.

### Metrics

- Structured query validity rate.
- Unsupported-intent false positive rate.
- Degraded response honesty rate.

### Regression

- Run a fixed scenario pack on every prompt or schema change.
- Replay timeout and empty-result mocks before release.

## Delivery plan

### Phase 1. Contracts

Freeze input/output/failure contracts with the UI and API consumers.

### Phase 2. Runtime

Implement schema lookup, validation, and bounded retry logic.

### Phase 3. Eval and ops

Add scenario regression, tracing, and degraded-path dashboards.

### Observability

- Log request class, selected filters, and contract path.
- Track schema lookup latency and timeout rate.

### Change management

- Version prompt and contract changes together.
- Require regression rerun before deployment.
