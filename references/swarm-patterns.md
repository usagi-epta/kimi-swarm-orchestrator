# Swarm Orchestration Patterns

Composable building blocks for coordinating multiple agents. Mix and match these patterns based on task structure — no single pattern fits all scenarios.

---

## Table of Contents

- [Pattern Overview](#pattern-overview)
- [Sequential Pipeline](#sequential-pipeline)
- [Parallel Fan-Out](#parallel-fan-out)
- [Stage-Gated Workflow](#stage-gated-workflow)
- [Executor + Evaluator Pairing](#executor--evaluator-pairing)
- [Fan-Out / Fan-In](#fan-out--fan-in)
- [Iterative Refinement Loop](#iterative-refinement-loop)
- [Dependency Chain Patterns](#dependency-chain-patterns)
- [Error Handling and Recovery](#error-handling-and-recovery)
- [Context Management Patterns](#context-management-patterns)
- [Anti-Patterns](#anti-patterns)

---

## Pattern Overview

These patterns are composable building blocks, not rigid templates. A real-world orchestration often combines 2-3 patterns: e.g., Fan-Out to parallel research, Sequential Pipeline to process each branch, then Fan-In to merge results.

**Selection criteria:**

| Factor | Pattern Direction |
|--------|-----------------|
| Tasks have dependencies? | Sequential, Dependency Chain |
| Tasks are independent? | Parallel Fan-Out |
| Quality gates needed? | Stage-Gated, Executor+Evaluator |
| Large task with partitions? | Fan-Out / Fan-In |
| Output needs polish? | Iterative Refinement |

Each pattern below is self-contained. Read only the patterns you need.

---

## Sequential Pipeline

Execute steps in strict order, each depending on the previous output.

```
Agent A --> Agent B --> Agent C --> Agent D
  output    output     output     final
```

### When to Use

- Dependencies exist between stages (B needs A's output)
- Order inherently matters (outline before chapters)
- Output of each stage feeds the next

### When NOT to Use

| Situation | Why Avoid |
|-----------|-----------|
| All tasks are independent | Wastes time vs. parallel execution |
| Latency is critical | Sequential adds cumulative latency |
| No stage-to-stage data flow | Unnecessary coupling |

### Example Scenario

Report generation:
1. `planner-report` — creates outline and chapter assignments
2. `writer-ch01` through `writer-ch05` — writes chapters using the outline
3. `editor-final` — reviews and polish

### Implementation

**plan.md dependency notation:**

```markdown
## Pipeline: Annual Report

1. **planner-report** → produces `outline.json`
2. **writer-ch01** → consumes `outline.json`, produces `ch01.md`
3. **writer-ch02** → consumes `outline.json`, produces `ch02.md`
4. **editor-final** → consumes `ch01.md` + `ch02.md`, produces `report-final.md`

Dependencies: planner-report → [writer-ch01, writer-ch02] → editor-final
```

**Orchestrator dispatch pattern:**

```markdown
Agent `writer-ch01`: Write Chapter 1 using this outline:
---
{{outline.json}}
---
Produce ch01.md, 1500-2000 words. Return only the chapter content.

[AWAIT writer-ch01]

Agent `writer-ch02`: Write Chapter 2 using the same outline:
---
{{outline.json}}
---
Note: Chapter 1 covers {{ch01_summary}}. Avoid overlap.
Produce ch02.md. Return only the chapter content.

[AWAIT writer-ch02]

Agent `editor-final`: Merge and polish these chapters:
- {{ch01.md}}
- {{ch02.md}}

Produce report-final.md with consistent voice and formatting.
```

---

## Parallel Fan-Out

Dispatch multiple independent tasks simultaneously.

```
         +---> Agent A ---+
Orchestrator ---> Agent B ---+---> (results collected)
         +---> Agent C ---+
```

### When to Use

- Subtasks are truly independent (no shared mutable state)
- No ordering constraints between agents
- You need speed over sequential guarantees

### When NOT to Use

| Situation | Why Avoid |
|-----------|-----------|
| Tasks read/write same files | Race conditions, data corruption |
| One task needs another's output | Dependency violation |
| Shared mutable context | Non-deterministic results |

### Concurrency Limits

| Context | Max Parallel Agents | Rationale |
|---------|-------------------|-----------|
| Quick research queries | 4-6 | Low token cost, high latency win |
| Code generation tasks | 3-4 | Moderate token cost, context growth |
| Document writing | 2-3 | High token output, manage context |
| Analysis on large inputs | 2 | Context window pressure |

**Rule of thumb:** If total output across parallel agents exceeds 8k tokens, reduce parallelism or use Fan-Out / Fan-In with intermediate aggregation.

### Example Scenario

Research three market segments simultaneously:

```markdown
Agent `researcher-ecom`: Research e-commerce trends in Southeast Asia 2024.
Produce: top 5 trends, growth rates, key players. Max 800 words.

Agent `researcher-fintech`: Research fintech adoption in Southeast Asia 2024.
Produce: top 5 trends, growth rates, key players. Max 800 words.

Agent `researcher-logistics`: Research logistics innovation in Southeast Asia 2024.
Produce: top 5 trends, growth rates, key players. Max 800 words.

[DISPATCH researcher-ecom, researcher-fintech, researcher-logistics]
```

### Implementation

**Single-turn multi-dispatch pattern:**

```markdown
Orchestrator dispatches N agents in one turn. Each agent receives:
- Its specific task
- Shared context (read-only) relevant to all
- Isolated output file path

No agent should depend on another agent's output in the same fan-out batch.
```

**plan.md notation:**

```markdown
## Parallel: Market Research

- **researcher-ecom** → `ecom-trends.md` [PARALLEL]
- **researcher-fintech** → `fintech-trends.md` [PARALLEL]
- **researcher-logistics** → `logistics-trends.md` [PARALLEL]
```

---

## Stage-Gated Workflow

Sequential stages with explicit quality gates between them.

```
Stage 1 --> [GATE 1] --> Stage 2 --> [GATE 2] --> Stage 3
          pass/fail            pass/fail
```

### When to Use

- Quality-critical outputs (code, legal text, public-facing content)
- Each stage has objective acceptance criteria
- Rework cost of downstream stages is high

### Gate Definition

A gate is a binary decision with explicit criteria:

```markdown
## Gate: Code Generation Stage

**Criteria:**
1. All functions have docstrings
2. No hardcoded values (all configurable)
3. Unit tests pass (exit code 0)
4. Lint score >= 8.0/10

**Decision:**
- PASS → proceed to Stage 2 (Integration)
- FAIL → retry Stage 1 with feedback

**Max retries:** 2 (then escalate to human)
```

### Gate Failure Handling

| Failure Severity | Action | Example |
|-----------------|--------|---------|
| Minor fixable | Retry same agent with feedback | Missing docstring |
| Major structural | Reassign to different agent | Wrong architecture |
| Repeated failure | Escalate (human review) | Failed 3 attempts |
| Dependency failure | Stop pipeline, reassess | Upstream broke contract |

### Example Scenario

Code generation pipeline:

```markdown
Stage 1: **generator-api** writes API endpoints
  Gate 1: Tests pass? [YES] → proceed

Stage 2: **integrator-db** adds database layer
  Gate 2: Integration tests pass? [NO] → retry with feedback
  [Retry #1] **integrator-db** fixes connection pool issue
  Gate 2: Integration tests pass? [YES] → proceed

Stage 3: **reviewer-security** security review
  Gate 3: No critical vulnerabilities? [YES] → DEPLOY
```

### Implementation Pattern

```markdown
Orchestrator: Dispatch `generator-api` with spec.
[AWAIT generator-api]

Orchestrator: Run test suite against output.
[Gate 1] Tests pass? → No → retry generator-api with failure log.
                    → Yes → proceed.

Orchestrator: Dispatch `integrator-db` with API code.
[AWAIT integrator-db]

Orchestrator: Run integration tests.
[Gate 2] Integration tests pass? → No → retry with feedback.
                                 → Yes → proceed.
```

---

## Executor + Evaluator Pairing

Dispatch a worker and a reviewer simultaneously for high-stakes outputs.

```
Task --> Executor A (works) --+--> Output
                              |
         Evaluator B (reviews) --> [PASS / REVISE / REJECT]
```

### When to Use

- High-stakes outputs (public docs, production code)
- Objective quality criteria exist
- You want quality assurance without sequential blocking

### Non-Blocking Reviewer Pattern

The evaluator reviews the current output while the executor (or next executor) proceeds with the next task. This avoids idle waiting:

```
Turn 1: Executor writes Section 1
Turn 2: Executor writes Section 2  |  Evaluator reviews Section 1
Turn 3: Executor writes Section 3  |  Evaluator reviews Section 2
Turn 4: (done)                   |  Evaluator reviews Section 3
```

If the evaluator returns REVISE, the executor must circle back — but Sections 2+ may be done in parallel.

### Handling REVISE Decisions

| Evaluator Verdict | Orchestrator Action |
|-------------------|-------------------|
| PASS | Store result, continue pipeline |
| REVISE | Dispatch **new sub-agent** with fix instructions (never fix inline) |
| REJECT | Mark task failed, consider re-decomposition |

**Never fix inline.** The orchestrator delegates fixes to a dedicated agent. This preserves audit trails and allows parallel work to continue.

### Example Scenario

```markdown
Executor `writer-blog`: Write blog post on Kubernetes networking.
[DISPATCH writer-blog]

Evaluator `reviewer-content`: Review for:
- Technical accuracy (all commands tested?)
- Tone (professional, not marketing-speak)
- Completeness (covers CNI, Services, Ingress?)

Return: PASS, REVISE [specific sections], or REJECT [reason].
[DISPATCH reviewer-content]  // parallel to next task if possible

[On REVISE]: Agent `writer-blog-fix`: Fix these issues:
- Line 45: kubectl command uses deprecated flag
- Section 3: Add explanation of headless services
```

---

## Fan-Out / Fan-In

Split work across agents, then merge results into unified output.

```
          +---> Agent A ---+
Input --> +---> Agent B ---+---> Merger --> Unified Output
          +---> Agent C ---+
```

### When to Use

- Large tasks with natural partitions (document sections, data chunks)
- Each partition can be processed independently
- Final output requires unified voice/format

### Merge Requirements

The merge step is **not** mechanical concatenation. The merger agent must:

1. **Resolve cross-references** (Section 1 mentions Section 3's topic)
2. **Unify voice and tone** (one writer may be formal, another casual)
3. **Remove duplication** (partition boundaries may overlap)
4. **Verify completeness** (all partitions present, nothing dropped)

### Consistency Checks

```markdown
Merger `integrator-report`: Merge these sections into final_report.md:
- {{section-intro.md}}
- {{section-analysis.md}}
- {{section-recommendations.md}}

Before merging, verify:
1. Terminology is consistent (e.g., "user" vs "customer" throughout)
2. Section references resolve (e.g., "as discussed in Section 3" points correctly)
3. Formatting matches template.md
4. Total word count within +/- 10% of target

Return: merged report + consistency_check.md listing any issues found.
```

### Example Scenario

Process a 100-page legal document:

```markdown
Fan-Out:
- **extractor-clauses** → extract all liability clauses (pages 1-30)
- **extractor-terms** → extract termination conditions (pages 31-60)
- **extractor-payment** → extract payment terms (pages 61-100)

Fan-In:
- **merger-legal** → unified summary with cross-references
```

---

## Iterative Refinement Loop

Repeated improvement cycles until quality threshold is met.

```
Draft --> [Gate] --> REVISE --> Improved Draft --> [Gate] --> ... --> PASS
```

### When to Use

- Output needs polish beyond single-pass generation
- Quality criteria are subjective or multi-dimensional
- Feedback from review can be actioned systematically

### Termination Conditions

Define **both** conditions before starting the loop:

| Condition | Purpose | Example |
|-----------|---------|---------|
| Pass gate | Natural completion | Reviewer scores >= 8/10 |
| Max iterations | Safety limit | Stop after 3 rounds |

**Always set a max.** Without it, you risk infinite loops on subjective criteria ("still not quite right").

### Anti-Pattern: Infinite Refinement

```markdown
BAD: "Keep improving until it's perfect"
GOOD: "Max 3 iterations. Gate: reviewer scores >= 8/10 on all 5 criteria"
```

### Example Scenario

```markdown
Round 1:
  Agent `writer-whitepaper` produces draft v1
  Agent `reviewer-tech` scores: accuracy=9, clarity=6, completeness=8
  Gate: clarity < 8 → REVISE (focus: clarity)

Round 2:
  Agent `writer-whitepaper` produces draft v2 (clarity improvements)
  Agent `reviewer-tech` scores: accuracy=9, clarity=8, completeness=8
  Gate: all >= 8 → PASS

Stop. Return draft v2.
```

### Implementation

```markdown
iterations = 0
max_iterations = 3
gate_passed = false

while not gate_passed and iterations < max_iterations:
    if iterations == 0:
        draft = dispatch(writer, task)
    else:
        draft = dispatch(writer, task + "\nFeedback: " + review_feedback)
    
    review = dispatch(reviewer, draft)
    gate_passed = check_gate(review.scores)
    iterations += 1

if not gate_passed:
    log_warning("Max iterations reached without passing gate")
    return draft + "\n[WARNING: Did not pass quality gate]"
```

---

## Dependency Chain Patterns

Manage complex task graphs with directed acyclic graphs (DAGs).

### DAG Structure

```
          +--> B --+
    A --> |        +--> E --> F
          +--> C --+
          |
          +--> D -------+
                        +--> G
          H ------------+
```

- **A** must complete before B, C, D start
- **E** must wait for B and C
- **F** depends only on E
- **G** waits for D and H
- **H** is independent until G

### Critical Path Identification

The critical path is the longest dependency chain — it determines minimum completion time:

```
Paths:
  A → B → E → F  (4 agents)
  A → C → E → F  (4 agents)
  A → D → G      (3 agents)
  H → G          (2 agents)

Critical path: A → B/C → E → F (4 stages)
Parallelizable: D and H run alongside B/C
```

### plan.md Dependency Notation

```markdown
## Task: Build Microservice

### Agents
- **scaffold** (`scaffold-svc`): Generate project structure
- **api** (`api-dev`): Implement REST endpoints
- **db** (`db-dev`): Set up database layer
- **auth** (`auth-dev`): Add authentication
- **test** (`test-engineer`): Write integration tests
- **deploy** (`deploy-ops`): Create deployment config

### Dependencies
```
scaffold --> [api, db, auth] --> test --> deploy
                    \___________/
                         |
                         v
                    (all three needed)
```

Explicit:
- api.depends_on = [scaffold]
- db.depends_on = [scaffold]
- auth.depends_on = [scaffold]
- test.depends_on = [api, db, auth]
- deploy.depends_on = [test]
```

### Example: 6-Agent Dependency Graph

```
plan.md:

Phase 1 (parallel after scaffold):
  scaffold → api (endpoints)
  scaffold → db (schema + migrations)
  scaffold → auth (middleware)

Phase 2 (gate: all Phase 1 complete):
  [api, db, auth] → test (integration tests)

Phase 3 (gate: tests pass):
  test → deploy (k8s manifests)

Phase 4 (parallel to deploy):
  deploy → docs (API documentation)
```

---

## Error Handling and Recovery

### Single Agent Failure

```markdown
Agent `api-dev` failed with: "Context window exceeded"

Options:
1. RETRY — same agent, same task (transient issue)
2. REASSIGN — different agent (agent-specific issue)
3. ESCALATE — human intervention (ambiguous failure)
4. SKIP + DEGRADE — continue without this output (if non-critical)
```

| Failure Type | Action | Example |
|-------------|--------|---------|
| Transient (timeout, rate limit) | Retry with backoff | API rate limited |
| Context overflow | Reassign with chunked input | 50k token input |
| Output format error | Retry with stricter prompt | Returned prose not JSON |
| Repeated failure (3x) | Escalate | Agent consistently fails |

### Multiple Agent Failure

When 2+ agents in a parallel batch fail:

1. **Stop** the pipeline
2. **Assess** if the decomposition is wrong
3. **Re-decompose** into finer or different subtasks
4. **Resume** with new decomposition

```markdown
Parallel batch: [researcher-ecom, researcher-fintech, researcher-logistics]
Result: researcher-ecom FAILED, researcher-fintech FAILED

Action:
1. Log: "2/3 research agents failed — likely task too broad"
2. Re-decompose: Split each research topic into 2 sub-topics
3. New agents: [researcher-ecom-seo, researcher-ecom-ux, ...]
4. Resume with new batch
```

### Partial Failure (Fan-Out / Fan-In)

```markdown
Fan-Out: 5 section writers
Result: 3 succeeded, 2 failed

Action:
1. Collect 3 successful outputs
2. Flag 2 missing sections in plan.md
3. Fan-In with partial results + explicit gaps:
   "Section 3 and 5 are missing due to agent failure.
    The remaining sections are complete."
4. Optionally: Dispatch new agents for missing sections only
```

### Timeout Handling

Set explicit timeouts per agent type:

| Task Type | Timeout | Action on Timeout |
|-----------|---------|-------------------|
| Research query | 2 min | Retry once, then reassign |
| Code generation | 3 min | Retry with simpler prompt |
| Document writing | 5 min | Split into smaller chunks |
| Analysis | 4 min | Retry with reduced scope |

### Context Overflow Handling

When an agent fails with context window exceeded:

1. **Chunk the input** — split into smaller pieces
2. **Progressive disclosure** — send metadata first, detail only when needed
3. **Fork context** — create a new agent with reduced context

```markdown
Agent `doc-analyzer` failed: input too large (40k tokens)

Fix:
1. Split document into 3 chunks (A: pages 1-10, B: 11-20, C: 21-30)
2. Dispatch `analyzer-chunk-a`, `analyzer-chunk-b`, `analyzer-chunk-c`
3. Fan-In: `synthesizer` merges partial analyses
```

---

## Context Management Patterns

### Chunking Strategies

| Strategy | Use When | Example |
|----------|----------|---------|
| Fixed-size chunks | Uniform content (logs, data) | Every 1000 lines |
| Semantic chunks | Variable content (documents) | By section/chapter |
| Hierarchical chunks | Deeply nested content | Top-level first, drill down |

### Progressive Disclosure

Send context in layers, expanding only when needed:

```markdown
Layer 1 — Metadata (always send):
  "Document: 50 pages, 5 sections, topic: API design"

Layer 2 — Summary (send on request):
  "Section summaries: [1] Overview, [2] REST principles, ..."

Layer 3 — Detail (send for specific sections):
  "Full text of Section 3: Authentication..."
```

### Fork vs. Pass Inline

| Approach | When to Use | When NOT to Use |
|----------|-------------|-----------------|
| **Fork** (new agent) | Context fundamentally changes direction | Task is trivial continuation |
| **Pass inline** | Sequential continuation of same task | Current context is irrelevant |

```markdown
Fork: Analyzer discovers a bug → Fork to `debugger` agent (new context)
Pass inline: Writer finishes Section 1 → Continue with Section 2 (same context)
```

### Passing Upstream Outputs to Downstream

**Efficient approach** — pass summaries + references, not full outputs:

```markdown
Inefficient:
  downstream_agent receives: [full_output_1.md, full_output_2.md, ...]
  Result: context overflow

Efficient:
  downstream_agent receives:
    - Summary of output_1 (200 words) + reference to file
    - Summary of output_2 (200 words) + reference to file
    - Full text ONLY for sections relevant to downstream task
```

**plan.md context contract:**

```markdown
## Context Flow

Agent `writer-ch03` receives:
  - outline.json (full — needed for structure)
  - ch01-summary.md (200 words — awareness only)
  - ch02-summary.md (200 words — awareness only)
  - style-guide.md (full — needed for compliance)

Agent `editor-final` receives:
  - ch01.md through ch05.md (full — needed for integration)
  - consistency-checklist.md (full — needed for verification)
```

---

## Anti-Patterns

### 1. Agent Over-Provisioning

```markdown
BAD: 8 agents for a 500-word email
  - planner-email, writer-subject, writer-body, writer-sign-off,
    reviewer-tone, reviewer-grammar, editor-final, proofreader

GOOD: 2 agents
  - writer-email, reviewer-email
```

**Rule:** If coordination overhead exceeds the work itself, use fewer agents.

### 2. Parallelising Dependent Tasks

```markdown
BAD:
  Agent A: "Write the API specification"
  Agent B: "Implement the API" [PARALLEL with A]
  # B has no spec to implement against

GOOD:
  Agent A: "Write the API specification" → [AWAIT]
  Agent B: "Implement the API" [after A completes]
```

### 3. Skipping Quality Gates

```markdown
BAD: "Deploy looks good, skip the security review to save time"

Result: Vulnerability in production. Cost to fix: 100x the review time.

Rule: Gates exist because rework cost > gate cost. Never skip.
```

### 4. The Yes-Man Reviewer

```markdown
BAD: Reviewer that only ever returns PASS

Signs of a lenient reviewer:
- No REVISE decisions in 10+ reviews
- Vague feedback ("looks good")
- Scores always cluster at 8-10/10

Fix: Define specific, objective criteria. Require evidence for PASS.
```

### 5. Orchestrator Does the Work

```markdown
BAD: Orchestrator rewrites agent output inline

Orchestrator: "The code has a bug. Here's the fix: [rewrites function]"

GOOD: Orchestrator delegates the fix

Orchestrator: "Agent `fixer-bug`: Fix this function per review feedback:
  - Line 23: off-by-one error in loop bound
  - Line 45: missing null check"
```

The orchestrator coordinates. It never generates, writes, or fixes content.

### 6. Inconsistent Naming

```markdown
BAD:
  - writer-ch1, writer_ch2, WriterChapter3
  - api-dev, APIDeployer, api_test

GOOD:
  - writer-ch01, writer-ch02, writer-ch03
  - api-dev, deploy-api, test-api

Rule: kebab-case consistently. Role-qualifier-number format.
```

---

## Quick Reference Card

| Pattern | Key Signal | Orchestration Cost | Latency |
|---------|-----------|-------------------|---------|
| Sequential Pipeline | Order matters | Low | High (cumulative) |
| Parallel Fan-Out | Independent tasks | Low | Low |
| Stage-Gated Workflow | Quality gates needed | Medium | Medium |
| Executor + Evaluator | High-stakes output | Medium | Low (parallel) |
| Fan-Out / Fan-In | Large partitioned task | High | Medium |
| Iterative Refinement | Needs polish | High | High |
| Dependency Chain | Complex task graph | High | Depends on DAG |
