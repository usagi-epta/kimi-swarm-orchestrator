# System Design Patterns

> **Reference for swarm-orchestrator** — loaded during swarm planning phases, before implementation begins, and when architectural tradeoffs must be made explicit.

Convert vague product intent into explicit technical boundaries and contracts that survive implementation and change. Optimize for clear ownership, explicit invariants, and low coupling rather than premature distribution.

## When to Apply

- Decomposing a large task into service/module boundaries.
- Designing APIs before implementation.
- Making architectural tradeoffs with ADR-quality reasoning.
- Planning consistency, idempotency, and integration boundaries.

## Inputs to Gather

| Category | What to Capture |
|---|---|
| Goals | Business goals, user journeys, success criteria |
| Constraints | SLA, throughput, latency, audit, privacy, compliance, data retention |
| Existing boundaries | Shared data, integration points, current service/module layout |
| Failure expectations | Retry expectations around money, inventory, identity, messaging |
| Team context | Team topology, deployment constraints, ownership boundaries |

## Decomposition Workflow

1. Break the feature into use cases and state transitions.
2. Identify core nouns, aggregates, and decision points.
3. Identify where consistency must be strong vs. where eventual consistency is acceptable.
4. Separate commands from queries when that improves clarity — not by default.
5. Identify external actors and dependencies.
6. Decide the right boundary type:
   - `package` — smallest, shared codebase
   - `module` — compilation boundary, shared runtime
   - `bounded context` — inside a modular monolith
   - `separate service` — independent deploy/scale/own
7. Design API and event contracts only after domain boundaries are clear.

## Boundary Rules

| Rule | Rationale |
|---|---|
| Prefer module over service when deploy/scale/own pressure is weak | Services carry distributed tax |
| Shared database tables across service boundaries are a warning sign | Violates data ownership |
| Draw boundaries around invariants and ownership, not CRUD screens | Screens change; invariants endure |
| Distinguish reference data sharing from operational write ownership | Read replication ≠ write ownership |
| A boundary is real only if dependency direction, data ownership, and failure handling agree | All three must align |

## API Design Rules

- Start from consumer use cases, not internal data shape.
- Make idempotency, concurrency, versioning, and error semantics explicit.
- Choose synchronous request-response only when latency, consistency, and dependency reliability justify it.
- Prefer additive evolution and stable machine-readable codes.
- Classify the API surface: public, partner-facing, internal synchronous, or async event-driven. Each has different compatibility expectations.

## Consistency & Idempotency Planning

| Concern | Guidance |
|---|---|
| Strong consistency | Use where money, inventory, identity mutations live |
| Eventual consistency | Acceptable for reads, reports, notifications, cross-boundary sync |
| Read-your-write | If needed by UX, eventual consistency imposes hidden costs |
| Idempotency keys | Required for money and inventory operations |
| Retry semantics | Define who retries, what the max is, and what partial success means |

## Modeling Nuances (Kotlin + JVM)

| Pattern | When to Use |
|---|---|
| Sealed hierarchies | Genuinely closed state machines or domain outcomes |
| Value classes | Domain primitives when they improve clarity |
| DTOs | Transport shapes only; do not let them become the domain model |
| Nullability | Express meaning, not missing analysis |

## Architecture Traps

| Trap | Safer Alternative |
|---|---|
| "Microservice by default" | Modular monolith with strong boundaries |
| Event-driven without ownership/replay semantics | Clear owner + replay semantics first |
| Eventual consistency where read-your-write is needed | Strong consistency at the UX-critical boundary |
| Public API = internal orchestration API | Separate surfaces, separate compatibility rules |
| ADRs recording only the chosen option | Capture rejected alternatives and why they lost |
| Reporting boundaries dictating write ownership | Separate transactional and analytical boundaries |

## Advanced Boundary Nuances

- Anti-corruption layers are cheaper than pretending two bounded contexts share the same ubiquitous language.
- Team ownership, deployment cadence, and support rotation are architecture inputs. Ignore them only if the code remains single-team.
- Multi-tenant behavior, data residency, and audit obligations can force boundaries that pure domain language does not reveal.
- Event choreography without a clear owner for recovery becomes shared confusion. If no one owns correction, the boundary is weak.
- Some features deserve saga/process-manager modeling — only when the business truly spans separate consistency boundaries.

## Expert Heuristics

- If two modules change together for every feature, they are probably not separate bounded contexts yet.
- Prefer boundaries that reduce the number of concepts a team must hold in working memory during a single change.
- If an API contract must survive multiple client generations, design for behavioral compatibility, not only field-level compatibility.
- Write the failure story for each boundary. If the team cannot explain retries, compensation, and partial success, the design is not finished.

## Output Contract

Return these sections in every decomposition:

```
Problem framing       — use cases, constraints, unknowns
Proposed boundaries   — module/service decomposition and ownership
Consistency map       — transactions, idempotency, eventual consistency
API/event contracts   — principal commands, queries, error semantics
Tradeoffs             — why this shape is better than alternatives
ADR outline           — decision, options, rationale, follow-up risks
```

## Guardrails

- Do not propose microservices where a disciplined module boundary is sufficient.
- Do not ignore non-functional requirements because the feature narrative sounds simple.
- Do not mistake CRUD decomposition for domain decomposition.
- Do not design APIs before clarifying ownership and invariants.

## Cross-References

- See `project-context-ingestion.md` when the decomposition targets an existing codebase — ingest the current stack and structure before proposing new boundaries.
- See `documentation-workflow.md` when the decomposition output must be captured as an ADR or technical spec.
