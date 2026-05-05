# Project Context Ingestion

> **Reference for swarm-orchestrator** — loaded when a swarm agent starts work on an existing codebase, before proposing code changes, fixes, or architecture advice.

Build an accurate mental model of a repository before acting. Treat this as the default first step whenever work targets an existing project.

## When to Apply

- Starting work on an existing codebase.
- Understanding project structure and conventions.
- Identifying tech stacks, dependencies, and patterns.
- Building context before making changes, proposing fixes, or giving architecture advice.

## Inspect First

Read these files before any business code:

| File Category | Files to Read |
|---|---|
| Build files | `settings.gradle.kts`, root `build.gradle.kts`, module build files, `gradle.properties`, `gradle/libs.versions.toml`, Gradle wrapper properties |
| Config files | `application.yml`, `application.yaml`, `application.properties`, profile-specific variants |
| Code layout | Top-level package/module layout, representative controller, service, repository, config, and test classes |
| Runtime & delivery | `Dockerfile`, `docker-compose*.yml`, Kubernetes/Helm manifests, CI workflows, `.env.example`, deployment scripts |

Always inspect dependency and plugin declarations before recommending any new annotation, library, or framework API.

## Extract the Project Map

Record these dimensions:

| Dimension | What to Capture |
|---|---|
| Versions | Kotlin version, Spring Boot version, Spring Framework generation, Gradle version, JDK/toolchain version |
| Framework mode | MVC vs. WebFlux, servlet vs. netty |
| Persistence mode | JPA vs. JDBC vs. jOOQ vs. MyBatis vs. R2DBC, blocking vs. reactive |
| Test stack | Test framework, test database (H2 vs. Testcontainers), mocking approach |
| Compiler plugins | `plugin.spring`, `plugin.jpa`, `plugin.serialization`, KAPT, KSP |
| Module structure | Single-module, multi-module, modular monolith, service-per-repo |
| Architecture | Package boundaries, layer rules (`web → service → persistence`), hexagonal adapters |
| Configuration | Active profiles, property binding style, secret-loading patterns, conditional beans |

## Work Sequence

```
1. Start from build and config files         → Do not begin with business code
2. Infer compatibility constraints             → Treat as hard boundaries for all later suggestions
3. Map modules and responsibilities            → Note where HTTP, persistence, messaging, security, tests live
4. Identify framework mode                     → MVC vs. WebFlux, blocking vs. reactive, sync vs. coroutine
5. Identify trap markers                       → Missing plugins, version conflicts, mixed stacks
6. Summarize what matters for the task         → Do not dump a full file inventory
7. If incomplete, state missing evidence       → Continue with bounded assumptions
```

## Kotlin + Spring Trap Markers

| Signal | Interpretation |
|---|---|
| AOP annotations without `plugin.spring` | Kotlin classes may not be proxied correctly |
| JPA entities without `plugin.jpa` | No-arg constructors may fail |
| Explicit versions for Jackson, Hibernate, Netty, Logback in a Boot-managed build | Version conflicts likely; check BOM/catalog first |
| Mixed blocking and reactive in same request flow | Architectural smell unless intentionally modularized |
| Profile-fragmented configuration redefining same properties | Inconsistency risk at runtime |
| Both servlet and reactive starters present | Verify intent; usually a warning sign |
| `data class` with JPA/Hibernate | Hibernate requires no-arg constructors; verify `plugin.jpa` |
| `@Transactional`, `@Cacheable`, `@Async` with no Kotlin Spring plugin | Proxying may silently fail |

## Context Signals (Advanced)

| Signal | What It Changes |
|---|---|
| `javax.*` vs `jakarta.*` imports | Places the codebase on a migration timeline; changes which Spring/Hibernate advice is valid |
| Generated sources (OpenAPI, QueryDSL, jOOQ, protobuf, MapStruct) | Safe edits belong in source definitions, not generated code |
| `spring.jpa.open-in-view` enabled | Lazy loading works differently; affects transaction guidance |
| `spring.main.lazy-initialization` enabled | Startup behavior changes; affects bean availability assumptions |
| Config Server, Vault, Helm-templated config | Local files may not show the full runtime truth |
| Observability/tracing/correlation conventions | Affects controller, client, and incident advice |
| Schema ownership (owns schema / shared DB / outbox / CDC) | Changes migration and transaction guidance |
| Application modules vs. library modules | Libraries may intentionally avoid the Spring Boot plugin or `bootJar` |
| `buildSrc` or `build-logic` convention plugins | These override what module build files appear to declare |

## What to Produce

Return a compact project brief with these sections:

```
Stack                    → framework mode, persistence mode, test stack, build stack
Compatibility constraints → exact versions or explicit unknowns
Architecture map         → modules/packages and responsibility boundaries
Operational config       → profiles, property binding, runtime/secret conventions
Risk markers             → project-specific traps that invalidate generic advice
Next commands/files      → highest-value checks to run next
```

## Decision Rules

- Prefer facts from the repository over conventions from memory.
- If multiple modules disagree on versions or stack style, call it out explicitly — do not normalize it away.
- If build files and runtime code imply different approaches, treat that as a risk, not a detail.
- If the task is narrow, still inspect minimum build and config context before editing code.
- If another reference is invoked later, feed it the extracted constraints instead of rereading from scratch.

## Expert Heuristics

- If the repo mixes JPA and R2DBC or MVC and WebFlux, determine whether that is an intentional boundary by module or an accidental hybrid. Advice differs sharply between the two cases.
- If the repo uses Kotlin coroutines on top of blocking persistence, call out that this is still a blocking architecture unless the persistence layer is reactive.
- If multiple dependency authorities exist, rank them. The real source of truth may be the Spring Boot plugin, a version catalog, a company convention plugin, or a platform BOM.
- If tests use a different stack than production (e.g., H2 in tests, Postgres in production), note that explicitly — it invalidates many persistence assumptions.
- If the repo has no obvious architecture rules, report that as a constraint instead of inventing a clean architecture that the codebase does not follow.

## Guardrails

- Do not recommend APIs or annotations from a different Spring Boot major version than the project uses.
- Do not add dependencies without checking whether the project already gets them from a BOM, version catalog, or convention plugin.
- Do not assume MVC when `spring-boot-starter-webflux` or coroutine-web stack is present.
- Do not assume JPA just because a database exists. Verify the actual persistence technology.
- Do not propose architecture refactors before identifying the current structure and team conventions.

## Cross-References

- See `system-design-patterns.md` when context ingestion reveals boundary or decomposition opportunities.
- See `documentation-workflow.md` when the ingested context needs to be documented as a project brief or onboarding guide.
