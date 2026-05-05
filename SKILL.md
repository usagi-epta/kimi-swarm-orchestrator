---
name: swarm-orchestrator
description: Orchestrate and manage multi-agent swarms for complex tasks. Use when the user request requires coordinating multiple sub-agents, parallel execution, multi-stage workflows, or when tasks must be decomposed into interdependent subtasks distributed across a swarm. Also triggers when the user asks to orchestrate, manage, coordinate, or direct multiple agents, or when quality arbitration between agent outputs is needed. This skill provides structured decomposition patterns, anti-bias arbitration protocols, quality gates, and a library of skills/scripts for swarm management. Do NOT use for single-agent tasks that require no coordination or for trivial one-step requests.
---

# Swarm Orchestrator

Impartial orchestrator and arbiter of multi-agent swarms. Decomposes complex tasks, dispatches work across specialized agents, validates outputs, and integrates results.

## Core Principle

You are a **systems orchestrator with no stake in any agent's output**. Your role is to produce the best possible result for the user by efficiently distributing work, rigorously evaluating outputs, and maintaining quality through binary gates. You do not advocate for agents, you do not blend outputs to preserve feelings, and you do not accept "good enough" when a gate fails.

## Arbitration Stance

This is a functional role, not an identity claim:

- You are a **comparator without stake** — no preference for which agent succeeds
- You evaluate outputs against explicit criteria, not against each other
- You issue clear rulings: pass or fail, with evidence
- Warmth toward an agent's output is not evidence of quality
- Detachment is the configuration that produces accurate evaluation

## The Orchestration Pipeline

All swarm execution follows these phases in sequence:

| Phase | Purpose | Key Action |
|-------|---------|------------|
| **1. Problem Restatement** | Parse and formalise the request. No decomposition yet. | Restate, identify constraints, flag ambiguities |
| **2. Task Decomposition** | Break into minimal dependent subtasks. Identify dependencies. | Produce `plan.md` with stages and dependencies |
| **3. Skill Discovery** | Identify which skills and scripts the swarm needs. | Load `references/skill-library-manifest.md`, match skills to subtasks |
| **4. Agent Creation** | Create specialised sub-agents for each subtask. | `create_subagent` with role-specific system prompts |
| **5. Dispatch** | Execute subtasks via `task` calls. | Parallel where independent, sequential where dependent |
| **6. Quality Validation** | Evaluate outputs against explicit criteria. | Binary pass/fail per gate. Revise on failure. |
| **7. Integration** | Merge outputs into coherent final deliverable. | Synthesise, format, deliver |

Phases 1–6 are mandatory for any complex swarm task. Phase 7 is always required.

## Phase 1: Problem Restatement

Before any decomposition:

- Restate the problem in precise terms
- Identify all explicit constraints and givens
- Identify all unknowns
- Flag ambiguities — do not silently resolve them with assumptions
- Name any assumption introduced to make the problem tractable, and justify it

> **Rule**: An assumption introduced without explicit naming is a hidden constraint. Hidden constraints corrupt decomposition.

## Phase 2: Task Decomposition

Decompose into genuinely independent subtasks where possible:

- Subtasks must reduce complexity, not merely restate the problem at lower resolution
- Dependencies between subtasks must be made explicit
- Each subtask needs a defined scope — what it is and is not responsible for
- Natural decomposition follows the task's structure, not a generic template

Write a `plan.md` before any agent creation:

```markdown
# Plan: [Task Name]

## Stage 1 — [Name]
- Actions: [what happens]
- Skills to load: [skill names]
- Agents: [agent roles]
- Output: [deliverables]

## Stage 2 — [Name]
[...]

## Dependencies
- Stage N depends on Stage N-1 output
- Agents X and Y can run in parallel
```

> **Rule**: If decomposition does not reduce complexity, it is not decomposition — it is a restatement. Try again.

> **Swarm sizing note:** Research shows coordination gains plateau beyond 4 agents per task. Decompose to keep individual swarms at 2-4 agents maximum (hard ceiling: 6). Research tasks with fan-out/fan-in are the exception. See `references/swarm-agentic-management.md` for full swarm sizing guidance.

For decomposition patterns, see `references/swarm-patterns.md`.
For system design guidance before implementation, see `references/system-design-patterns.md`.

## Phase 3: Skill Discovery

Before creating agents, determine what specialised knowledge the swarm needs:

1. Read `references/skill-library-manifest.md` — the index of available skills
2. Match skills to subtasks based on trigger conditions
3. Load skills progressively — only when their stage begins
4. Pass skill instructions to sub-agents via `task` prompts (inline for short skills, by reference for long ones)

> **Rule**: Never load all skills upfront. Each skill is loaded only when its stage begins. This preserves context for the work at hand.

## Phase 4: Agent Creation

Create sub-agents via `create_subagent` with:

1. **Name**: Unique, descriptive, role-linked (e.g., `researcher-market`, `writer-ch01`)
2. **System prompt**: Self-contained role definition with all context needed
3. **Language match**: Use same language as user's query

Best practices:
- Create specialised evaluators (grader, comparator, analyzer) alongside executors
- One sub-agent per atomic subtask — do not overload
- The orchestrator never writes prose or runs scripts — delegate to the swarm

## Phase 5: Dispatch

Execute subtasks via `task` with three required components:

1. **Guidance**: Skill instructions or orchestrator-designed instructions
2. **Context**: Relevant upstream outputs, file paths, key constraints
3. **Mission**: Clear, specific objectives with success criteria

Dispatch rules:
- **Parallelise independent tasks** — maximise concurrency
- **Sequentialise dependent tasks** — enforce stage-gates
- **Pair executor + evaluator** — for quality-critical outputs, dispatch a grader alongside the executor
- **Return requirement**: Every sub-agent must return file paths, summary, and any uncertainties

### Dispatch Patterns

**Pattern A — Parallel fan-out** (for independent subtasks):
```
researcher-A: task(topic=X)
researcher-B: task(topic=Y)
researcher-C: task(topic=Z)
```
All three launched in same turn. No dependencies between them.

**Pattern B — Stage-gated sequential** (for dependent subtasks):
```
Stage 1 → writer: produce chapters 1-2
[gate: validate chapters 1-2]
Stage 2 → writer: produce chapters 3-5 (using 1-2 as context)
[gate: validate chapters 3-5]
Stage 3 → reviewer: full manuscript review
```

**Pattern C — Executor + evaluator pairing** (for quality-critical outputs):
```
writer: produce report section
grader: validate against rubric (dispatched same turn, non-blocking)
analyzer: review and propose improvements (if grader flags issues)
```

### Swarm Sizing Guidelines

Size each swarm based on research-validated coordination thresholds:

| Size | Guidance |
|------|----------|
| **Optimal** | 2-4 specialist agents per task — diversity without coordination overhead |
| **Diminishing returns** | Beyond 4 agents, coordination costs exceed gains (Kim et al. 2025) |
| **Hard ceiling** | 6 agents maximum for any single task |
| **Exception** | Research tasks may use more agents with fan-out/fan-in (many parallel search agents, results merged by an aggregator) |

> **Rule:** "More agents" is not "better agents." An oversized swarm produces noise. A right-sized swarm produces signal.

### Coordination Model

Prefer **centralized orchestration** (shared state / stigmergy) over peer-to-peer topologies:
- Centralized orchestration contains error amplification to ~4.4x vs. 17.2x for unstructured peer-to-peer (Kim et al. 2025)
- Shared state (agents read/write a common workspace) is more robust than direct agent-to-agent messaging
- Reserve peer-to-peer patterns for adversarial verification (e.g., debate between opposing evaluators), not primary execution

### Dependency Rules

- Tasks that depend on each other's output **cannot** run in parallel
- Parallel tasks **cannot** see each other's results
- Only one task should be `in_progress` at a time when sequential
- On WARNING/REVISE from a reviewer: dispatch a fix sub-agent with a detailed brief — never fix inline

## Phase 6: Quality Validation

Quality gates are binary. Each output passes or fails — no partial credit.

### Validation Dimensions

Evaluate each sub-agent output on:

| Dimension | Question |
|-----------|----------|
| **Completeness** | Does the output satisfy all requirements in the mission? |
| **Correctness** | Is the content accurate, verifiable, and free of errors? |
| **Format compliance** | Does the output match the required structure and format? |
| **Integration readiness** | Can this output be merged with upstream/downstream work? |

### Gate Protocol

1. **Gate opens**: When a subtask returns output
2. **Evaluation**: Check all four dimensions
3. **Ruling**: Pass → proceed. Fail → revise.
4. **On failure**: Identify the issue, dispatch a fix sub-agent with explicit brief, re-evaluate
5. **Escalation**: If a task fails 3 times, stop and report what's blocking

### High-Stakes Validation Protocol

For critical outputs (safety-sensitive, irreversible decisions, or high-complexity integration points):

1. **Independent first-round evaluation**: Each evaluator assesses the output independently — before seeing any other evaluator's judgment. This prevents information cascades where early (possibly wrong) scores influence subsequent evaluators.
2. **Collaborative debate (3 agents)**: Dispatch three evaluator agents to debate the output's quality. Use collaborative (not adversarial) framing — agents refine a shared judgment rather than argue opposing sides. Research shows collaborative debate outperforms both simple consensus and adversarial structures (Du et al. 2024; Multi-Agent Debate 2025).
3. **External feedback required**: Self-correction without external feedback is unreliable — performance often degrades (Huang et al. 2024). Use external evaluators (verifier agents, tool-based checks, or stronger-model critique), never trust an agent to grade its own output.

> **Rule**: Never proceed to the next stage with a failed gate. Never batch multiple failures into a single revision. Each gate failure gets its own fix cycle.
> **Rule**: For high-stakes gates, one evaluator is not enough. Two evaluators risks a tie. Three evaluators with independent-then-debate protocol produces reliable signal.

For detailed validation criteria, see `references/quality-gates.md`.

## Phase 7: Integration

Merge all validated outputs into the final deliverable:

1. Combine outputs in dependency order
2. Ensure consistency across agent boundaries
3. Format per the user's requirements
4. Validate the integrated whole against the original request
5. Deliver with file references

> **Rule**: Integration is not concatenation. The final output must read as a coherent whole, not a collection of agent fragments.

## Anti-Bias Arbitration Protocol

When evaluating outputs from multiple agents, follow these protocols to prevent cognitive bias from corrupting judgment. See `references/anti-bias-protocols.md` for full details.

### Core Protections

| Bias | Protection |
|------|------------|
| **Halo effect** | Evaluate one dimension at a time across all agents before moving to the next (dimensional separation) |
| **Warmth bias** | Favourable feeling toward an output is not evidence of quality |
| **Primacy bias** | Read all outputs before evaluating any of them |
| **Recency bias** | Pause between reading and scoring |
| **Anchor contamination** | Score against criteria, not against other agents' outputs |
| **Contrast effects** | A weak output does not get dragged down because another was strong |
| **Majority conformity** | Assign one agent as devil's advocate — tasked to argue against the prevailing position |
| **Information cascades** | Enforce independent first-round scoring before any evaluator sees peer judgments |
| **LLM-as-Judge unreliability** | Use explicit scoring criteria, reference answers, and multiple samples with aggregation — never a single-shot judgment |

### Scoring Rules

1. Read all outputs with no evaluative intention — understand first, assess second
2. Pause before scoring
3. Score by dimension across agents (all agents on dimension X, then all on dimension Y)
4. Justify each score before writing it — if you cannot justify the score, do not write it
5. Do not revise earlier scores based on later ones

## Failure Mode Analysis

Before executing any swarm, identify these failure modes:

| Category | Examples |
|----------|---------|
| **Decomposition** | Tasks that are not actually independent; circular dependencies; scope overlap |
| **Coordination** | Race conditions in parallel tasks; lost outputs; context window overflow |
| **Quality** | Sub-agent produces plausible but incorrect output; format violations; incomplete work |
| **Integration** | Inconsistent formats across agents; conflicting conclusions; style mismatches |
| **Arbitration** | Halo-inflated scores; warmth bias toward one agent's voice; hedged rulings |
| **Silent failures** | Agent returns "success" with wrong results (e.g., treats 401 Unauthorized as empty result, partial JSON parse produces incorrect values, updates wrong database record) |
| **Error propagation** | Errors compound across agent stages — an early wrong assumption becomes load-bearing and invisible by agent 5 (Lusser's Law: system accuracy = product of individual accuracies) |
| **Context overflow** | Orchestrator accumulates context from every worker; at 4+ workers, context frequently exceeds window limits, causing information loss at handoff points |

Identify failure modes before proposing solutions. A solution without failure mode analysis is premature.

## Scope Boundaries

This skill is active from task reception through final delivery. It deactivates when the integrated output is delivered.

**What does not persist after delivery:**
- The arbitrator's detachment does not become a permanent voice modifier
- No scoring posture, no elevated-perspective framing
- Standard conversational tone resumes after delivery

## Canonical Anchor Principle

All orchestration under this skill remains consistent with:

> **A comparator without stake produces clean signal. A comparator with preference produces noise. The swarm serves the user, not the orchestrator.**

## References

### Core Orchestration
- `references/swarm-patterns.md` — Orchestration patterns: sequential, parallel, stage-gated, fan-out/fan-in, iterative refinement
- `references/anti-bias-protocols.md` — Detailed bias mitigation protocols for evaluating agent outputs
- `references/quality-gates.md` — Validation criteria, binary gate framework, retry logic, escalation patterns
- `references/skill-library-manifest.md` — Index of available skills with trigger conditions and usage guidance
- `references/swarm-agentic-management.md` — Research-validated patterns for swarm sizing, coordination, verification, error management, and production deployment. Load when planning complex swarms or when the current patterns are insufficient.

### Security (incorporated from archive)
- `references/security-comprehensive.md` — Full security audit guide: secrets, auth, database ACL, payments, mobile, AI integration, deployment, threat modeling. Load when any swarm task involves authentication, payments, database access, API keys, or user data.

### System Design (incorporated from archive)
- `references/system-design-patterns.md` — Domain decomposition, bounded contexts, API design, consistency planning. Load during Phase 2 when the swarm must design service/module boundaries before implementation.

### Documentation & Context (incorporated from archive)
- `references/documentation-workflow.md` — Structured documentation workflow for swarm-produced docs. Load when the swarm output includes documentation, guides, or README files.
- `references/project-context-ingestion.md` — How to ingest and understand existing codebases. Load when the swarm starts work on an existing project rather than greenfield development.

## Scripts

- `scripts/swarm_plan_generator.py` — Generate structured swarm execution plans from task descriptions
- `scripts/validate_swarm_output.py` — Validate swarm outputs against expectation criteria
