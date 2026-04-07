# Agent development methodology

This document is derived from `Инженерия агентов 2026`, mainly the sections about instructions, agent requirements, and IDEF0. Its purpose is to provide a compact but engineering-grade reference for reading the dashboard and the audit package.

## 1. An agent is not an LLM

An LLM alone is not an agent. It is a stochastic inference engine that interprets text and predicts tokens. An agent starts where an execution environment appears around the model:

- memory;
- tools;
- constraints;
- orchestration;
- output contract;
- eval and observability.

Without those layers, you have a request-response interface to a model, not an agent system.

## 2. Two development loops

Agent development naturally splits into two coupled loops.

### Engineering loop

This loop owns:

- architecture and component boundaries;
- tool and API integrations;
- runtime loop;
- scalability and reliability;
- observability;
- reproducibility and operations.

Without it, even a strong prototype remains “magic” that cannot be operated safely.

### Research loop

This loop owns:

- role design;
- reasoning style;
- SOP;
- constraints;
- input/output formats;
- eval datasets and error analysis.

Without it, the system may be formally correct but behaviorally useless.

Good agent work keeps both loops alive. Engineering without research produces empty automation. Research without engineering produces a fragile prompt prototype.

## 3. The minimum unit of design

Practical rule:

> Agent = one business function.

Not “a smart assistant”, not “an agent that does everything”, but one function with a clear trigger, clear constraints, and a defined product.

This matters because:

1. One function can be tested.
2. One function can have a stable output contract.
3. One function can have a clear responsibility boundary.

If a request cannot be expressed as a single atomic function, the correct response is decomposition into multiple agents or a supervisor plus sub-agents.

## 4. IDEF0 as the requirement frame

Agent requirements are easier to reason about through IDEF0.

### Input

What starts the function:

- a user request;
- an event;
- a file;
- a handoff from another agent.

Input design is not just a list. It must cover request classes, edge cases, and invalid states.

### Control

What governs the behavior:

- role / identity;
- SOP;
- constraints;
- output contract;
- decision rules.

This is the primary control layer. It turns stochastic model behavior into a narrow corridor of allowed actions.

### Mechanism

What the agent uses to execute:

- tools;
- runtime;
- memory;
- sandbox;
- sub-agents;
- integrations.

Mechanism should not bleed into control. A prompt should not carry low-level API details, retry counts, or other implementation details that belong in code and configuration.

### Output

What counts as completion:

- success;
- business-empty;
- technical failure;
- partial / refusal;
- delegation.

The output must be treated as an interface, not as “some useful text”.

## 5. What must exist in the control layer

### Identity & Goal

The agent must know:

- who it is;
- which single function it performs;
- who consumes the result.

Single Responsibility Principle matters here. Broad roles almost always create behavioral drift.

### SOP

The SOP is the procedural core:

- entry conditions;
- ordered steps;
- branches;
- stop conditions;
- tool-use rules.

A good SOP makes the agent behave like natural-language pseudocode. A weak SOP leaves too much room for improvisation.

### Constraints

Constraints define what the agent must never do:

- invent data;
- reinterpret a technical error as a business result;
- drift out of role;
- use tools outside the allowed scenario.

Constraints primarily align the model with business logic.

### Output contract

An agent is a function, so its output should behave like an API contract:

- machine-readable;
- validatable;
- stable across runs;
- not limited to the happy path.

If the output is not typed, the agent integrates poorly and becomes hard to test.

## 6. Context is an engineering problem

Context engineering exists to avoid stuffing everything into one prompt.

### Static context

The immutable part:

- system rules;
- policies;
- tone of voice;
- tool descriptions;
- domain base knowledge.

### Dynamic context

The changing part:

- the current request;
- conversation history;
- tool outputs;
- runtime state;
- date and time.

### Four context-management techniques

- **Write**: move long intermediate artifacts into external state.
- **Select**: inject only the context that is relevant right now.
- **Compress**: reduce raw tool outputs to the signal the model actually needs.
- **Isolate**: separate responsibilities through sub-agents and sandboxing.

## 7. Engineering hygiene

A prompt is a development artifact.

That implies:

- keep it in the repository;
- review it;
- version it;
- compose it from modules;
- run regressions after edits.

Changing one line in a prompt can alter the system as much as changing one line of code.

## 8. What eval must cover

An agent cannot be trusted on a couple of happy-path examples.

Eval must cover:

- positive scenarios;
- edge cases;
- business-empty outcomes;
- tool failures;
- partial / refusal paths;
- incorrect routing;
- constraint violations.

The dataset should contain not only “nice” examples but also the cases most likely to break the logic.

## 9. Practical minimum requirement set

Before implementation, an agent should have at least:

1. One clear business function.
2. An IDEF0 description: input / control / mechanism / output.
3. Role + SOP + constraints.
4. A typed output contract.
5. A tool list and tool-use policy.
6. Edge-case understanding.
7. Eval scenarios.
8. Basic operational signals.

Without these artifacts, teams usually fall back to prompt tuning by intuition.
