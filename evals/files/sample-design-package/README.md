# Unit design (RoleFrame methodology)

The package shows an implementation-ready design with a clear control/mechanism split. The main remaining work is operational hardening and regression coverage.

## Files

- `01_catalog-query-designer.md`

## Summary

| Unit | Readiness | Level | Primary risk | First phase |
|---|---:|---|---|---|
| `catalog-query-designer` | 74/100 | Implementation-ready draft | Observability and regression coverage are still thinner than the control and contract design. | Phase 1. Contracts |

## Critical risks

- Schema drift can invalidate the generated query contract.
- Timeout handling is designed but not yet instrumented in production.
- Regression coverage must include unsupported-intent and degraded-path cases.
