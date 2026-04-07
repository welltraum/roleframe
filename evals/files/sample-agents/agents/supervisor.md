---
name: supervisor
description: Routes tax authority requests across sub-agents and returns a final response.
temperature: 0.1
tools:
  toolkits:
    - docs-search
sub_agents:
  - document-finder
  - response-drafter
middleware:
  - type: retry
---
You are the supervisor for tax authority requests.

{{supervisor}}
