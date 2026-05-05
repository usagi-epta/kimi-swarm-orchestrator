# Quality Gates Reference

Binary checkpoints in the swarm pipeline. Each gate is **pass** or **fail** — no partial credit, no "mostly passes." Purpose: prevent defective outputs from propagating downstream.

## Table of Contents

- [The Four Validation Dimensions](#the-four-validation-dimensions)
- [Gate Types](#gate-types)
- [The Gate Protocol](#the-gate-protocol)
- [Retry Logic](#retry-logic)
- [Escalation Patterns](#escalation-patterns)
- [Integration Gate (Phase 7)](#integration-gate-phase-7)
- [Gate Templates](#gate-templates)
- [Metrics to Track](#metrics-to-track)
- [Anti-Patterns](#anti-patterns)

---

## The Four Validation Dimensions

Every gate evaluates against these four dimensions. An output must satisfy all four to pass.

### Completeness

| Check | Description |
|---|---|
| Requirements enumerated | Every requirement from the mission is listed as a checklist item |
| All sections addressed | No missing sections, unaddressed criteria, or incomplete work |
| Depth verified | Hard requirements receive the same treatment as easy ones |
| Edge cases covered | Boundary conditions, error paths, and exceptions are handled |

**Checklist procedure:**
1. Enumerate every requirement from the mission
2. Verify each requirement has a corresponding output section
3. Flag any requirement marked "nice to have" — it is still a requirement

**Common failure:** Output addresses the easy parts, omits the hard parts.

**Example:** Mission requires implementing OAuth + rate limiting + audit logging. Output has full OAuth and rate limiting but audit logging is a `// TODO` comment. → **FAIL** on completeness.

---

### Correctness

| Check | Description |
|---|---|
| Facts verifiable | All factual claims can be traced to a source |
| Code executable | Code compiles, runs, and produces expected output |
| Logic sound | Reasoning chains are valid; no circular or false logic |
| Citations valid | Every citation resolves and supports the claim it is attached to |

**Common failure:** Plausible-sounding but incorrect information — confident wrong answers are more dangerous than obvious errors.

**Example:** Output states "Python's GIL was removed in 3.10." → **FAIL** on correctness. The GIL remains in CPython as of 3.12+; it can be optionally disabled via `--disable-gil` in 3.13+ free-threaded builds, but was not removed.

---

### Format Compliance

| Check | Description |
|---|---|
| Structure matches | Output follows the required file format, schema, or template |
| Naming conventions | File names, variable names, identifiers follow project conventions |
| Section order | Required sections appear in the specified sequence |
| Metadata present | Frontmatter, headers, version tags, or other boilerplate are included |

**Common failure:** Correct content in wrong format — the answer is right but unusable.

**Example:** API spec delivered as a Markdown narrative instead of an OpenAPI 3.0 YAML file. Content is accurate, format is non-compliant. → **FAIL** on format compliance.

---

### Integration Readiness

| Check | Description |
|---|---|
| Interface consistency | Naming conventions, data structures, and signatures match upstream/downstream contracts |
| Style alignment | Code style matches the project (lint, formatter config) |
| Dependency compatible | New dependencies do not conflict with existing ones |
| Mergeable | Output can be integrated without manual conflict resolution |

**Common failure:** Output that works in isolation but breaks the pipeline when merged.

**Example:** Agent A outputs a TypeScript module using camelCase interfaces. Agent B, downstream, expects PascalCase interfaces per project convention. Neither is wrong alone; together they fail. → **FAIL** on integration readiness.

---

## Gate Types

Three severity levels determine the consequence of failure.

| Type | Behavior | Action on Failure |
|---|---|---|
| **Hard Gate** | Non-negotiable. Failure blocks all downstream work. | Stop. Fix. Re-validate before proceeding. |
| **Soft Gate** | Warning. Proceeding allowed with acknowledgment. | Log issue, proceed with caution, schedule fix in next iteration. |
| **Informative Gate** | Observation. No pass/fail. | Record metrics for process improvement. |

### Hard Gate — Examples

- Security vulnerability (unescaped user input, leaked secrets)
- Broken build (compilation error, missing dependency)
- Data corruption (malformed output, encoding error)
- Contract violation (API incompatible with consumer)

**Agent behavior on failure:**
```
STATUS: BLOCKED
REASON: Hard gate "security-scan" failed — secret detected in env.example
ACTION: Redact secret, re-run scan, confirm clean
NEXT: Re-validate at Gate 3 before proceeding to Gate 4
```

### Soft Gate — Examples

- Style deviation (tabs vs. spaces, line length > 120)
- Minor format issue (missing trailing newline, inconsistent header levels)
- Non-critical missing element (secondary docstring, optional example)
- Performance below threshold but not catastrophic

**Agent behavior on failure:**
```
STATUS: PROCEEDING WITH WARNING
REASON: Soft gate "style-check" — 4 lint violations in test files
ACTION: Log violations to fix-queue, proceed to downstream agent
NEXT: Address in polish pass; does not block integration
```

### Informative Gate — Examples

- Token usage per agent
- Execution time by phase
- Agent workload distribution (which agents handled what)
- Retry counts and failure frequency

**Agent behavior:**
```
STATUS: OBSERVATION
METRIC: phase-3 agent consumed 4,200 tokens, 2 retries
ACTION: Recorded to session log for capacity planning
```

---

## The Gate Protocol

The stage-gated workflow (see `swarm-patterns.md`) uses this validation procedure at each stage boundary.

| Step | Action | Actor |
|---|---|---|
| 1 | Gate opens. Upstream task signals completion. | Orchestrator |
| 2 | Load evaluation criteria for this gate. | Orchestrator |
| 3 | Evaluate output against all four dimensions. | Validator agent |
| 4 | Issue ruling: `PASS`, `FAIL`, or `WARN`. | Validator agent |
| 5 | If `PASS` → close gate, propagate output downstream. | Orchestrator |
| 6 | If `FAIL` → stop pipeline, dispatch fix agent, return to Step 3. | Orchestrator |
| 7 | If `WARN` → log warning, proceed with note, schedule fix. | Orchestrator |

### Gate State Machine

```
        OPEN
         |
         v
    [Evaluate] -----> FAIL ----> [Fix] ----> [Evaluate]
         |                         |
         |                         v
         |                      Escalate (3 retries)
         |
         +-----> WARN ----> [Log] ----> Proceed
         |
         +-----> PASS ----> Close ----> Downstream
```

**Rules:**
- A gate cannot be skipped. It can be fast-tracked (pre-validated outputs) but the evaluation step must run.
- Only one gate is open per branch at any time.
- A gate closed with `PASS` is immutable — downstream work depends on it.
- Re-opening a closed gate triggers downstream invalidation (all dependent gates reopen).

---

## Retry Logic

| Rule | Value | Rationale |
|---|---|---|
| Maximum retries per gate | 3 | Prevents infinite loops; forces escalation |
| Retry reset condition | Only after a fix is applied | No blind retries |
| Fix requirement | Explicit fix instructions: what changed and why | Ensures each retry is a genuine attempt, not a dice roll |
| Progressive strategy | Fix → re-evaluate → if still failing, broaden scope | Avoids retrying the same narrow fix repeatedly |

### Progressive Retry Strategy

| Attempt | Scope | Tactic |
|---|---|---|
| 1 | Narrow | Fix the specific failure point; clearer instructions |
| 2 | Medium | Refactor surrounding context; re-examine assumptions |
| 3 | Broad | Re-decompose the task; try a different agent or approach |

**Example:**
```
Attempt 1: "Fix the null pointer on line 47 in parseConfig()"
  → FAIL: same issue

Attempt 2: "Refactor parseConfig() to use defensive checks throughout.
            The config object may be partially populated."
  → FAIL: config object shape is wrong

Attempt 3: "Re-decompose: separate config validation from config parsing.
            Assign a new agent to validate the expected schema first."
  → If FAIL → Escalate
```

---

## Escalation Patterns

Each failure triggers an escalation tier. Do not retry indefinitely at the same tier.

| Failure Count | Action | Instruction Change |
|---|---|---|
| **First failure** | Retry with same agent | Clarify instructions; add explicit constraints |
| **Second failure** | Retry with different agent or modified decomposition | Change the agent, change the decomposition, or both |
| **Third failure** | **Stop. Report blocker. Request human decision.** | Do not retry again without human input |
| **Cascade failure** | Multiple gates failing simultaneously | Reassess the plan — this signals a decomposition error |

### Cascade Failure Detection

A cascade failure is defined as **two or more independent gates failing within the same phase**.

| Signal | Interpretation |
|---|---|
| Multiple agents fail completeness | The mission may be under-decomposed |
| Multiple agents fail integration readiness | Interface contracts are ambiguous or undefined |
| Mixed dimension failures | The decomposition may be assigning wrong agents to wrong tasks |

**Action on cascade failure:**
1. Halt all parallel work in the affected phase
2. Do not retry individual agents — the plan is flawed
3. Return to decomposition phase
4. Re-examine mission boundaries and agent assignments

---

## Integration Gate (Phase 7)

The Integration Gate is a **hard gate** that sits at the boundary between swarm execution and user delivery. It validates the merged output against the **original user request** — not against any intermediate specification.

| Check | What It Validates |
|---|---|
| Fidelity to original request | The merged output satisfies what the user actually asked for |
| Cross-agent consistency | No contradictions between sections produced by different agents |
| Information preservation | Nothing was lost, dropped, or mangled during integration |
| Format compliance (final) | The delivered artifact matches the expected output format |

**Integration Gate is the final quality bar.** If it fails, the swarm has not done its job regardless of how many upstream gates passed.

**Example failure:** Three agents produce accurate sections on authentication, database schema, and API design. The integration agent merges them into a single document. The Integration Gate checks against the original request — "a deployment guide for the authentication service" — and discovers the merged document is a design spec, not a deployment guide. → **FAIL**. All three upstream agents passed their individual gates; the mission was misaligned with the user's intent.

---

## Gate Templates

Ready-to-use templates. Copy and adapt for each project.

### Code Output Gate

| # | Check | Gate Type |
|---|---|---|
| 1 | Compiles/runs without errors | Hard |
| 2 | Passes relevant tests (unit, integration) | Hard |
| 3 | Follows style guide (linter/formatter clean) | Soft |
| 4 | Security scan clean (no secrets, no injection paths) | Hard |
| 5 | Documentation complete (docstrings, README if public) | Soft |
| 6 | No known dependencies with CVEs | Hard |
| 7 | Correctness verified against requirements | Hard |
| 8 | Integration tests pass with downstream consumers | Hard |

**Quick-check prompt:**
```
Evaluate this code output against:
1. Does it compile/run without errors? (Y/N)
2. Do all tests pass? (Y/N)
3. Are there any security issues? (Y/N — if Y, list them)
4. Does it match the style guide? (Y/N — if N, list violations)
5. Does it fully implement the requirements? (Y/N — if N, list gaps)
```

---

### Document Output Gate

| # | Check | Gate Type |
|---|---|---|
| 1 | All required sections present | Hard |
| 2 | Facts verified against sources | Hard |
| 3 | Format matches template or project convention | Soft |
| 4 | Grammar and style correct | Soft |
| 5 | Cross-references valid (links, citations, footnotes) | Hard |
| 6 | No internal-only content exposed (paths, keys, internal URLs) | Hard |
| 7 | Tone appropriate for audience | Soft |

**Quick-check prompt:**
```
Evaluate this document against:
1. List every required section. Is each present? (Y/N per section)
2. For every factual claim: cite source. (Pass/Fail per claim)
3. Does the format match the template? (Y/N)
4. Are there grammar or style errors? (Y/N — if Y, quote them)
5. Are all cross-references resolvable? (Y/N — if N, list broken ones)
6. Does any content expose internal systems? (Y/N)
```

---

### Research Output Gate

| # | Check | Gate Type |
|---|---|---|
| 1 | Sources cited and accessible (URLs resolve, papers retrievable) | Hard |
| 2 | Claims supported by evidence (each claim traces to a source) | Hard |
| 3 | No contradictions with known facts or between sources | Hard |
| 4 | Coverage of all requested dimensions | Hard |
| 5 | Timestamp/current as of execution date | Informative |
| 6 | Confidence level stated for uncertain conclusions | Soft |

**Quick-check prompt:**
```
Evaluate this research output against:
1. For each claim: what source supports it? (List source per claim)
2. Are all sources accessible? (Y/N — if N, flag them)
3. Are there internal contradictions? (Y/N — if Y, quote the conflict)
4. Does it cover every dimension in the research brief? (Y/N per dimension)
5. Is there a timestamp or "as of" date? (Y/N)
```

---

### Creative Output Gate

| # | Check | Gate Type |
|---|---|---|
| 1 | Meets creative brief requirements (subject, length, constraints) | Hard |
| 2 | Original (not plagiarized; distinct from input references) | Hard |
| 3 | Appropriate tone and style for the target medium | Soft |
| 4 | Technical constraints satisfied (character limits, format specs) | Hard |
| 5 | Brand guidelines followed (if applicable) | Soft |

**Quick-check prompt:**
```
Evaluate this creative output against:
1. Does it satisfy every item in the creative brief? (Y/N per item)
2. Is it substantively original compared to the references? (Y/N)
3. Is the tone appropriate? (Y/N — if N, describe the mismatch)
4. Are technical constraints met? (Y/N — if N, list violations)
```

---

## Metrics to Track

Optional but recommended for process improvement.

| Metric | What to Measure | Why It Matters |
|---|---|---|
| Gate pass rate per agent type | % of gates each agent type passes on first attempt | Identifies weak agent configurations |
| Average retry count per gate type | Mean retries for hard gates, soft gates, integration gate | Flags brittle gates or unclear criteria |
| Time in validation vs. execution | Ratio of validation time to work time | Reveals if gates are too heavy |
| Common failure reasons | Top 3 failure reasons per gate dimension | Drives targeted process improvements |
| Cascade failure frequency | Count of multi-gate failures per phase | Signals decomposition quality |
| Integration gate pass rate | % of sessions that pass the final gate | Ultimate quality indicator |

**Tracking format:**
```
Session: <id>
Gate-1 (completeness): PASS (agent: codegen-1, retries: 0)
Gate-2 (correctness):   FAIL → retry 1 → PASS (agent: codegen-1, retries: 1)
Gate-3 (integration):   PASS (retries: 0)
Integration Gate:       PASS
Total validation time:  45s
Total execution time:   3m 12s
```

---

## Anti-Patterns

Common mistakes that undermine gate integrity.

| Anti-Pattern | Description | Fix |
|---|---|---|
| **Moving the goalposts** | Changing criteria after evaluation starts | Lock criteria at gate open; criteria changes require reopening the gate from Step 1 |
| **Grade inflation** | Accepting "mostly passes" or "close enough" as pass | Enforce binary rulings; if in doubt, **FAIL** and retry |
| **Skipping gates to save time** | Bypassing validation because "it's probably fine" | Gates are mandatory; skipping a gate invalidates all downstream guarantees |
| **Running gates too early** | Validating partial output before the agent signals completion | Gate opens only when upstream declares completion; premature evaluation is wasted effort |
| **Running gates too late** | Validating after downstream work has already consumed the output | Gate closes before downstream begins; late gates can trigger expensive invalidation cascades |
| **Inconsistent criteria** | Same gate type uses different checks across sessions | Gate templates are versioned; use the same template for the same gate type every time |
| **Retry without change** | Re-submitting the same output hoping for a different result | Each retry must document what changed and why; no-change retries are automatic **FAIL** |
| **Silent soft-gate escalation** | Treating repeated soft-gate failures as acceptable | Three soft-gate warnings for the same issue on the same output escalate to a hard gate |

---

*This reference pairs with `swarm-patterns.md` (stage-gated workflow pattern) and `SKILL.md` (swarm-orchestrator skill definition).*
