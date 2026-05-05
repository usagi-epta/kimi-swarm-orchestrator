# Swarm Agentic Management: Unified Reference for Multi-Agent Orchestration

> **Version:** 1.0 | **Sources:** Academic, Industry, Cognitive Science, State-of-the-Art |
> **Audience:** Swarm orchestrator agents using `create_subagent` and `task` tools |
> **Principle:** Every claim cites its supporting research stream(s). When evidence conflicts, the stronger evidence prevails.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Swarm Sizing and Composition](#2-swarm-sizing-and-composition)
3. [Coordination Architecture](#3-coordination-architecture)
4. [Quality Verification and Arbitration](#4-quality-verification-and-arbitration)
5. [Debiasing Protocols](#5-debiasing-protocols)
6. [Error Management](#6-error-management)
7. [Production Patterns](#7-production-patterns)
8. [Observability and Debugging](#8-observability-and-debugging)
9. [Anti-Patterns](#9-anti-patterns)
10. [Integration Cheat Sheet](#10-integration-cheat-sheet)

---

## 1. Executive Summary

These are the highest-impact findings supported by two or more independent research streams.

- **[CRITICAL] Agent count saturates at 3-4 agents per task.** Coordination gains plateau beyond 4 agents; adding more produces diminishing returns and increased error amplification. Evidence: SOTA (Science of Scaling, R^2=0.89 cross-validation), Academic (CJT network generalizations), Industry (Beam.ai production data). Decompose large tasks into sub-tasks with 3-4 agents each rather than scaling a single swarm.

- **[CRITICAL] Unstructured agent networks amplify errors up to 17.2x; centralized orchestration contains this to 4.4x.** "Bag of agents" peer-to-peer topologies without governance are the single highest-risk architecture. Evidence: SOTA (Kim et al. 2025, 180 controlled configurations), Academic (MAEBE peer-pressure dynamics), Industry (production failure analysis).

- **[CRITICAL] LLMs cannot self-correct reasoning without external feedback.** Intrinsic self-correction at inference time often degrades performance. Effective correction requires external signals: tool outputs, unit tests, stronger-model critiques, or human input. Evidence: SOTA (Huang et al. ICLR 2024, replicated across 6+ domains), Cognitive (overconfidence epidemic, ECE up to 74%), Academic (debate convergence to wrong answers).

- **[CRITICAL] Always separate generation from verification agents structurally.** Agents that both generate and judge their own work exhibit severe overconfidence (ECE 15-74%). Verification must be performed by agents with different model families, different prompts, or both. Evidence: Cognitive (LLM-as-a-Fuser, JudgeBench), SOTA (MAST taxonomy: 21% of failures are verification gaps), Academic (Tool-MAD: 18.5% improvement with tool-augmented verification).

- **[HIGH] Enforce independent evaluation before any cross-agent communication.** Information cascades form after just 2-3 consecutive agents express the same (possibly wrong) view. Independent first-round evaluation prevents sycophancy and cascade effects by 40-60%. Evidence: Cognitive (Bikhchandani et al. 1992; CONSENSAGENT), Academic (CJT independence violation), SOTA (error propagation as contagion dynamics).

- **[HIGH] Collaborative multi-agent debate outperforms adversarial debate for judgment tasks, and both outperform simple majority voting.** Fixed-round debate wastes compute; use adaptive termination (Beta-Binomial + KS-test). Evidence: SOTA (Du et al. 2024; 4-7% improvement over majority), Academic (adversarial framing outperforms cooperative for generation, but NOT for judgment), Cognitive (anti-conformity guardrails required).

- **[HIGH] Stigmergy (shared state over direct messaging) reduces token overhead 80% while maintaining coordination.** Direct O(N^2) messaging explodes bandwidth; shared artifacts agents write-to and read-from are the dominant production pattern. Evidence: Academic (80% token reduction production report), Industry (LangGraph StateGraph, CrewAI shared memory), Cognitive (distributed cognition: Hutchins 1995).

- **[HIGH] Durable execution (checkpointing) is the critical differentiator between prototype and production.** Without it, crashed 45-minute tasks restart from scratch, re-consuming all tokens and time. Evidence: Industry (LangGraph checkpointers, Temporal.io, Azure Durable Task), Academic (hierarchical LLM multi-agent frameworks with prompt optimization).

- **[HIGH] The MAST taxonomy identifies 14 failure modes across three categories.** 42% are specification problems, 37% are coordination failures, 21% are verification gaps. Use this as a pre-deployment audit checklist. Evidence: SOTA (Cemri et al. NeurIPS 2025, 1,600+ traces), Industry (production failure mode analysis).

- **[MEDIUM] Temperature > 0 and persona diversity produce measurably better emergent coordination.** Higher temperature increases beneficial diversity; persona conditioning and Theory-of-Mind prompting improve role specialization. Optimal: 3-5 agents at temperature 1.0. Evidence: SOTA (emergent coordination experiments), Academic (MAEBE framework, ToM prompting), Cognitive (Diversity Prediction Theorem).

---

## 2. Swarm Sizing and Composition

### 2.1 Optimal Agent Count Per Task

| Task Type | Recommended Agent Count | Evidence | Rationale |
|-----------|------------------------|----------|-----------|
| Simple generation (single modality) | 1 (best single agent) | Academic, SOTA | One-shot expert rule dominates for novel one-off tasks |
| Verification/quality check | 3 independent evaluators | Cognitive, SOTA | Minimum for reliable aggregation; diminishing returns beyond 3 |
| Complex multi-step reasoning | 3-4 specialist agents | SOTA, Academic, Industry | Coordination gains plateau at 4; error amplification increases |
| Collaborative debate/judgment | 3-7 agents (adaptive termination) | SOTA, Cognitive | Diminishing returns beyond 7; instability below 3 |
| Emergent coordination tasks | 3-5 agents at temp > 0 | SOTA, Academic | Each additional member decreases success odds by ~8% |
| Large-scale decomposition | Decompose into sub-tasks with 3-4 agents each | Academic, Industry, SOTA | Hierarchical decomposition beats flat scaling |

**The saturation threshold (SOTA: Kim et al. 2025; Academic: CJT bounds):**
- Below 4 agents: Adding agents measurably improves outcomes
- At 4 agents: Coordination gains plateau
- Above 4 agents: Coordination overhead consumes benefits; error amplification dominates
- At 10+ agents: Significant degradation in most configurations

### 2.2 When Adding Agents Helps vs. Hurts

```
HELPFUL conditions:
- Task has verifiable answers (enables majority voting)
- Agents are cognitively diverse (different models, temps, personas)
- Independence is preserved (no cross-communication before evaluation)
- Task rewards strategy diversity (emergent coordination)
- Iterative task with learning history (aggregated rules optimal)

HARMFUL conditions:
- One-shot novel task (expert rule dominates)
- Agents share training data/architecture (correlated errors violate CJT)
- Unstructured peer-to-peer topology (17.2x error amplification)
- Excessive communication bandwidth (>1200 bits overwhelms)
- One agent is clearly superior to others
```

### 2.3 Agent Diversity Requirements

**The Diversity Prediction Theorem** (Cognitive: Page) mathematically proves:
```
Collective Error = Average Individual Error - Prediction Diversity
```

More diversity directly reduces collective error. Operationalize diversity across these dimensions:

| Diversity Type | Implementation | Impact |
|---------------|---------------|--------|
| Model architecture | Mix GPT, Claude, Llama, Gemini families | Prevents correlated errors; highest priority |
| Temperature | Range 0.1-1.0 across agents | Increases response diversity; temp > 0 improves emergent coordination ~50% per unit |
| Persona/role | Assign distinct expert types (Researcher, Clinician, Teacher) | Improves alignment with human ratings; sharpens role differentiation |
| Evaluation rubric | Different metrics per agent (correctness, clarity, safety, style) | Prevents halo effect via dimensional separation |
| Prompt framing | Different system prompts for same task | Creates independent reasoning paths |

**Critical constraint:** Diversity of model architecture is the highest-impact dimension. Three agents from different families outperform three from the same family by 8-47% on judgment tasks (Cognitive: LLM-as-a-Fuser, JudgeBench).

### 2.4 Temperature/Diversity Settings by Swarm Type

| Swarm Type | Temperature Range | Rationale |
|-----------|------------------|-----------|
| Verification/evaluation | 0.1-0.3 per agent; ensemble across temps | Lower for consistency; diversity from model family mix, not temperature |
| Generation/creative | 0.5-1.0 | Higher for beneficial diversity; multiple candidates for aggregation |
| Emergent coordination | 1.0 | Each unit increase raises success odds ~50%; optimal at 1.0 |
| Debate/arbitration | 0.5-0.7 | Balance between diversity and coherence |
| Safety-critical | 0.1-0.2 | Lower temperature for consistency; compensate with model diversity |

---

## 3. Coordination Architecture

### 3.1 Centralized Orchestration vs. Peer-to-Peer

| Dimension | Centralized (Orchestrator-Worker) | Peer-to-Peer | Evidence |
|-----------|----------------------------------|--------------|----------|
| Error amplification | 4.4x (contained) | 17.2x (unstructured) | SOTA: Kim et al. 2025 |
| Scalability | Good (hierarchies extend) | Poor (O(N^2) messaging) | Academic, Industry |
| Latency | Lower (single decision point) | Higher (consensus rounds) | Academic, Industry |
| Best for | Well-understood, decomposable tasks | Verification, brainstorming, simulation | Academic: 3 consensus patterns |
| Failure mode | Orchestrator context overflow; single point of failure | Endless debate; emergent conformity | Industry, SOTA |

**Verdict:** Use centralized orchestration as the default. Reserve peer-to-peer for structured verification with explicit termination criteria (max 3-5 rounds).

### 3.2 Stigmergy Pattern (Shared State over Direct Messaging)

Stigmergy is the dominant coordination mechanism for production swarms. Agents do not message each other directly; they write to and read from shared artifacts.

```protocol
STIGMERGY PATTERN:
1. Initialize shared state (document, knowledge graph, structured record)
2. Each agent reads relevant state, performs work, writes results back
3. Coordinator monitors state changes; intervenes only on exceptions
4. State versions tracked for rollback/audit
5. All agents observe same ground truth; no message loss
```

**Evidence convergence:**
- Academic: 80% token reduction vs. direct messaging; "indirect communication through stigmergic traces is computationally advantageous, avoiding exponential growth of state-action spaces"
- Industry: LangGraph StateGraph, CrewAI shared memory, all production frameworks use shared state
- Cognitive: Hutchins' distributed cognition -- "the cognitive processes required to manipulate a tool are not the same as the computations performed by manipulating the tool"

**Implementation:**
- Use a central state store (Redis/PostgreSQL) with schema-enforced writes
- Each agent receives a read-only copy of state + its assigned slice
- Writes are atomic and versioned; conflicts resolved by orchestrator
- Shared state is the primary coordination mechanism; direct messages only for exceptions

### 3.3 Communication Bandwidth Guidelines

Three operating regimes exist (Academic: GVQ research, bandwidth-efficient multi-agent communication):

| Regime | Bandwidth | Success Rate | Use When |
|--------|-----------|-------------|----------|
| Bandwidth-limited | <400 bits | Low (13.8% baseline) | Highly independent subtasks |
| Balanced | 400-1200 bits | High (38.8%, +181% over no-comm) | Most multi-agent applications |
| Bandwidth-abundant | >1200 bits | Marginal improvement | Complex coordination requiring rich state |

**Operational rules:**
- Gate communication to meaningful behavior changes only
- Target the balanced regime for most applications
- Compress messages (semantic summaries); maintain overhead below 15%
- Metrics: message-to-task ratio, bandwidth utilization (<40%), overhead (<15%), semantic density

### 3.4 Hierarchical Decomposition Patterns

**The 2-3 layer hierarchy** (Academic: arXiv:2602.21670; Industry: production patterns):

```
LAYER 1: Strategic (Global Planner)
  - Decomposes user request into sub-tasks
  - Produces task DAG with dependency edges
  - Optimizes allocation using historical performance data

LAYER 2: Tactical (Type/Specialist Agent)
  - Manages execution of a sub-task category
  - Maintains meta-prompts accumulating learned constraints
  - Validates structured outputs before passing down

LAYER 3: Execution (Worker Agent)
  - Performs atomic operations
  - Returns structured results to Layer 2
  - Reports failures with structured error codes
```

**Task representation as DAG** (Academic: MDPI Applied Sciences):
- Four dependency types: internal (execution order), conditional, temporal (synchronization), resource constraints
- LLM generates structured DAG; heuristic optimizer allocates to agents
- Genetic Algorithm optimizes for workload balance, execution time, capability matching

**Key rule:** Flatten hierarchies where possible. Prefer 2 levels over 4. Each management level adds planning/delegation overhead and information-loss risk (Industry: hierarchical command pattern analysis).

---

## 4. Quality Verification and Arbitration

### 4.1 Collaborative Debate Pattern (3 Agents, Adaptive Termination)

Multi-agent debate consistently outperforms simple majority voting when properly structured.

```protocol
COLLABORATIVE DEBATE PROTOCOL:
1. Generate 5-7 diverse initial responses (diversity pruning: keep 5 most diverse)
2. Initialize 3 debate agents with distinct perspectives
3. Each round: agents observe full debate history, update positions
4. After each round: test for stability using Beta-Binomial mixture + KS statistic
5. Terminate when distribution stabilizes (prevents both premature stop and wasted compute)
6. Final output: synthesize from converged distribution, not select from candidates
```

**Performance data** (SOTA: Multi-Agent Debate 2025):

| Benchmark | Single Agent | Majority Vote | Collaborative Debate | Improvement |
|-----------|------------|---------------|----------------------|-------------|
| JudgeBench | 63.7% | 66.1% | 68.1% | +2-5% over majority |
| LLMBar | 76.7% | 77.8% | 81.8% | +4% over majority |
| TruthfulQA | 69.5% | 72.0% | 74.3% | +2-3% over majority |

**Critical design choice: Collaborative > Adversarial for judgment.** Adversarial debate (MAD) consistently underperforms collaborative debate across all benchmarks. Forcing equal consideration of correct and incorrect arguments gives the incorrect side equal opportunity to persuade. Use adversarial framing for generation tasks (find flaws), collaborative framing for judgment tasks (refine beliefs).

### 4.2 Why Adversarial Verification Beats Consensus Voting

| Mechanism | Problem | Evidence |
|-----------|---------|----------|
| Consensus voting | "Agents agreed on wrong things more often than disagreed on right things" | Academic: Talvinder field notes; SOTA: error cascade dynamics |
| Simple majority | Loses nuance; weighted by count not quality | Cognitive: LLM-as-a-Fuser; Academic: weighted reputation consensus |
| Adversarial verification | Structural separation of generation and verification functions; frame as "find flaws" | Academic: Tool-MAD +18.5%; Cognitive: ACH matrix; SOTA: MAST verification gaps |

**Key distinction:**
- **For generation tasks:** Use adversarial critique ("find flaws in this output")
- **For judgment/evaluation tasks:** Use collaborative belief refinement ("what is the most accurate assessment")
- **Never use simple majority vote** for high-stakes decisions; always use weighted or structured aggregation

### 4.3 LLM-as-Judge Best Practices

LLM evaluators are reliable only under strict design constraints (SOTA: Yamauchi et al. 2025; Cognitive: JudgeBench overconfidence data).

```protocol
LLM-AS-JUDGE PROTOCOL:
1. Provide explicit evaluation criteria AND reference answers in the prompt
2. Use score descriptions ONLY for highest and lowest scores (intermediate descriptions degrade reliability)
3. Sample multiple evaluations (temperature > 0) and aggregate by mean
4. Use 3-5 different judge models from different families
5. Randomize candidate order (position swap) across evaluations
6. Require confidence scores (0-1) with reasoning for each judgment
7. Track calibration metrics (ECE, TH-Score) per judge over time
```

**Calibration quality targets** (Cognitive: JudgeBench systematic evaluation):

| ECE Range | Assessment | Action |
|-----------|-----------|--------|
| <2% | Well-calibrated | Production target |
| 2-5% | Acceptable | Monitor for drift |
| 5-15% | Moderate miscalibration | Weight lower; trigger recalibration |
| 15-40% | Severe overconfidence | Do not use without external verification |
| >40% | Critical miscalibration | Remove from evaluation pool |

**Overconfidence is pervasive:** 14 SOTA LLMs tested; all cluster predictions at 90-100% confidence while achieving 60-80% accuracy. GPT-4o: ECE 39-47%. Mistral-Nemo: ECE up to 74%. Never trust uncalibrated confidence scores.

### 4.4 Structured Analytic Techniques

**Analysis of Competing Hypotheses (ACH)** (Cognitive: CIA tradecraft; operationalized for agent systems):

| Stage | Action | Agent Implementation |
|-------|--------|---------------------|
| 1. Hypotheses | Generate all plausible quality interpretations | Multiple agents propose competing hypotheses about output quality |
| 2. Evidence | List all significant evidence | Each agent independently identifies relevant evidence |
| 3. Diagnostics | Assess evidence diagnosticity | Use evidence that would DISPROVE a hypothesis, not confirm it |
| 4. Refinement | Consolidate matrix | Merge overlapping evidence and hypotheses |
| 5. Inconsistencies | Flag disconfirming evidence | Identify which hypothesis has most disconfirming evidence |
| 6. Sensitivity | Test robustness | Check if conclusions change when key evidence is interpreted differently |
| 7. Conclusions | Report probabilistic assessment | Output relative likelihood of each quality level with confidence |

**Red Teaming for Evaluation** (Cognitive: automated red-teaming research):
- Designate one agent specifically to find flaws in the majority evaluation
- Achieves 3.9x higher vulnerability discovery rate vs. manual red-teaming
- Use category-specific meta-prompts; hierarchical detection (lexical, semantic, behavioral)

**Devil's Advocate / Team B Analysis** (Cognitive: Janis groupthink prevention; CIA tradecraft):
1. Split evaluation agents into Team A (supports prevailing view) and Team B (argues against)
2. Each team develops its best case independently
3. Structured cross-examination of assumptions
4. Separate neutral jury evaluates both positions
5. Full audit trail of what was considered and why

### 4.5 Self-Correction Limitations -- Why External Feedback Is Required

**The core finding (SOTA: Huang et al. ICLR 2024, replicated across 6+ domains):**

LLMs cannot reliably self-correct reasoning using only inherent capabilities. Performance often *degrades* after self-correction attempts. Three reasons:

1. LLMs generate plausible but internally coherent errors that evade consistency-based detection
2. Without external ground truth, the model has no signal to distinguish correct from incorrect reasoning
3. "Knowing you made a mistake" and "knowing what the correct answer is" are different capabilities

**When self-correction works (external feedback required):**

| Feedback Source | Effectiveness | Example |
|---------------|-------------|---------|
| Code execution (unit tests) | Very High | Pass/fail signal is unambiguous |
| Tool output (search, calculator) | High | Ground truth from external system |
| Stronger model critique | High | GPT-4 evaluating GPT-3.5 output |
| Human feedback | Very High | Direct correction |
| Symbolic reasoner | Very High | Logic proof checker |

**The Re-ReST pattern** (SOTA: Ji et al. 2024): Distill self-correction capability into the model during training using external feedback, eliminating inference-time overhead. Results: +7.6% on HotpotQA, +28.4% on AlfWorld.

**Operational rule:** Never rely on an agent's self-assessment of its own output. Always route verification to a separate agent or external tool.

---

## 5. Debiasing Protocols

### 5.1 Independent First-Round Evaluation (Prevents Information Cascades)

Information cascades form when agents observe others' judgments before forming their own, causing them to discard private information and conform. Cascades activate after just 2-3 consecutive matching judgments.

```protocol
INDEPENDENT-THEN-AGGREGATE (ITA):
1. All N evaluators produce independent assessments with NO cross-communication
2. Each evaluator outputs: score, confidence (0-1), reasoning, potential biases noted
3. Only after all evaluations are complete, aggregate using weighted method
4. If confidence is low (<0.7) or disagreement high (variance > threshold), trigger structured debate
5. Weight earlier (independent) evaluations more heavily than later (potentially influenced) ones
```

**Evidence:** Reduces cascade effects by 40-60% vs. sequential evaluation (Cognitive: Bikhchandani et al. 1992; CONSENSAGENT results). Academic CJT requires independence; violating it degrades collective accuracy.

### 5.2 Dimensional Separation (Prevents Halo Effect)

A single positive or negative trait disproportionately colors the entire assessment (Thorndike 1920, confirmed across 100+ years of research).

```protocol
DIMENSIONAL SEPARATION:
1. Decompose evaluation into independent rubric dimensions:
   - Correctness (does it solve the problem?)
   - Clarity (is it understandable?)
   - Safety (are there harmful elements?)
   - Style (is formatting appropriate?)
2. Each dimension scored by a different agent or with a different prompt
3. Scores combined only after all dimensions are independently assessed
4. Prevents a "well-written but wrong" answer from scoring highly on correctness
```

**Additional mitigations:**
- **Blind evaluation:** Present outputs without revealing which model generated them
- **Position swapping:** Randomize candidate order across evaluations (confirmed across 100K+ instances)
- **Length normalization:** Explicitly instruct judges to value conciseness; normalize by response length

### 5.3 Devil's Advocate / Team B Analysis

Always include at least one agent tasked with arguing against the majority position.

```protocol
DEVIL'S ADVOCATE PROTOCOL:
1. Run standard Independent-Then-Aggregate evaluation
2. If consensus emerges (>66% agreement), activate devil's advocate agent
3. Devil's advocate receives: the consensus position, the evidence, and the instruction "find the strongest argument against this conclusion"
4. Devil's advocate produces counter-argument with supporting evidence
5. Original evaluators reconsider in light of counter-argument (second-chance review)
6. Final output: either confirmed consensus or documented uncertainty
```

**Evidence:** Janis's 9th prevention recommendation; CIA standard practice; ScienceDirect validation; reduces groupthink effects in controlled studies.

### 5.4 Calibration and Confidence Assessment

**Track calibration history per evaluator agent:**

| Metric | What It Measures | Target |
|--------|-----------------|--------|
| ECE (Expected Calibration Error) | Gap between confidence and accuracy | <5% for production use |
| TH-Score | Practical calibration in decision-relevant intervals | Higher is better; track trends |
| Brier Score | Overall probabilistic accuracy | Decompose into uncertainty, resolution, reliability |
| Per-task-type accuracy | Accuracy broken down by task category | Weight by recent performance with decay |

**Confidence-calibrated routing:**
- Well-calibrated agents (ECE <5%): high weight, auto-accept high-confidence evaluations
- Moderately calibrated (ECE 5-15%): medium weight, human review for borderline cases
- Poorly calibrated (ECE >15%): low weight, require external verification, schedule recalibration

**Superforecaster techniques for agents** (Cognitive: Tetlock et al. Good Judgment Project):
1. Outside view first: establish base rates for similar tasks before evaluating specifics
2. Dimensional decomposition: break complex evaluations into components
3. Probability elicitation: require numerical probability estimates, not just labels
4. Pre-mortem analysis: "Imagine this evaluation was wrong -- why?"
5. Reflection: post-evaluation metacognitive review of confidence quality

---

## 6. Error Management

### 6.1 Error Propagation Chain -- How Failures Compound

Error propagation follows **Lusser's Law** from systems engineering: system success is the product of individual success probabilities.

| # Agents | Per-Agent Accuracy | System Accuracy | Error Rate |
|----------|-------------------|-----------------|------------|
| 1 | 98% | 98.0% | 2.0% |
| 3 | 98% | ~94.1% | ~5.9% |
| 5 | 98% | ~90.4% | ~9.6% |
| 10 | 98% | ~81.7% | ~18.3% |

**Two distinct error mechanisms** (SOTA; Industry):

1. **Error accumulation:** Each agent assumes previous output is correct and builds on it. A wrong assumption becomes load-bearing and invisible by agent 5. **Fix:** Intermediate validation gates between every step.

2. **Confidence inflation:** As chains get deeper, outputs become more organized, authoritative, and well-formatted -- but coherence is not correctness. Each agent treats previous output as settled ground rather than probabilistic input. **Fix:** Independent critic agents at each stage; explicit uncertainty propagation.

### 6.2 Circuit Breakers and Containment Strategies

**Circuit breaker configuration** (Industry: production patterns):

| Component | Error Threshold | Time Window | Open Duration |
|-----------|----------------|-------------|---------------|
| LLM API calls | 50% error rate | 20 requests | 30s, exponential backoff, max 5min |
| Inter-agent communication | 30% error rate | 10 requests | 30s start, exponential backoff |
| Tool execution | 40% error rate | 15 requests | 60s for external tools |

**Fallback hierarchy for LLM failures:**
1. Retry with lower-tier model
2. Use cached responses for common queries
3. Fall back to rule-based responses
4. Queue for human review

**Containment strategies** (SOTA; Academic; Industry):

| Strategy | Effectiveness | When to Apply |
|----------|--------------|---------------|
| Validation gates between steps | Very High | Always; between every agent stage |
| Centralized orchestration | High (4.4x vs 17.2x) | Default architecture |
| Limit to 4 agents per task | High | When task permits decomposition |
| Genealogical tracing | High (debugging) | All production systems |
| Structured messaging (MCP/A2A) | Medium | Schema-enforced communication |
| Independent verification steps | Medium | Critical outputs |

### 6.3 Durable Execution Pattern (Checkpointing)

Without durable execution, a crashed 45-minute task must restart from scratch, re-consuming all tokens and time.

```pattern
DURABLE EXECUTION:
[Agent Start] --> [Step 1] --> [Checkpoint] --> [Step 2] --> [Checkpoint] --> [Step 3] --> [Complete]
                                              ^
                                              |
                              [Crash] --------+
                              [Resume from last checkpoint]
```

**Implementation options:**

| Technology | Backend | Best For |
|-----------|---------|----------|
| LangGraph Checkpointers | PostgreSQL, Redis, SQLite, MongoDB | Complex conditional workflows |
| Temporal.io | Durable workflow engine | Long-running business processes |
| Azure Durable Task | Automatic checkpointing | Microsoft ecosystem |
| DBOS (Pydantic) | SQLite persistence | Python-first workflows |

**Critical rule:** Implement durable execution from day one. The cost of adding it after a production incident is 10x the cost of building it in (Industry: production recommendations).

### 6.4 Trace-to-Eval Pipeline (Failures to Regression Tests)

The most important observability pattern for production agents:

```pipeline
[Production Failure] --> [Trace Capture] --> [Root Cause Analysis] --> [Eval Case Creation] --> [CI/CD Gate] --> [Blocked Regression]
```

1. Capture the full trace of the production failure (every turn, tool call, state change)
2. Analyze the causal chain to find the root step where behavior diverged
3. Convert the failing trace into a permanent evaluation case
4. Add to eval suite that runs on every PR
5. Future deployments are blocked if they would reintroduce the same failure

### 6.5 The MAST 14-Failure Taxonomy

The Multi-Agent System Failure Taxonomy (SOTA: Cemri et al. NeurIPS 2025), from 1,600+ execution traces across 7 frameworks:

**FC1: Specification and System Design Failures (41.77%)**
- FM-1.1: Disobey task specification
- FM-1.2: Disobey role specification
- FM-1.3: Step repetition
- FM-1.4: Loss of conversation history
- FM-1.5: Unaware of termination conditions

**FC2: Inter-Agent Misalignment (36.94%)**
- FM-2.1: Conversation reset
- FM-2.2: Fail to ask for clarification
- FM-2.3: Task derailment
- FM-2.4: Information withholding
- FM-2.5: Ignored other agent's input
- FM-2.6: Reasoning-action mismatch

**FC3: Task Verification and Termination (21.30%)**
- FM-3.1: Premature termination
- FM-3.2: No or incomplete verification
- FM-3.3: Incorrect verification

**Pre-deployment audit:** Check each failure mode against your architecture. FM-1.1 and FM-1.2 (specification violations) are the most common -- use JSON schema specifications and explicit constraints.

---

## 7. Production Patterns

### 7.1 Orchestrator-Worker Pattern

```
[Orchestrator Agent] --decompose--> [Worker A] --results--+
     |                                [Worker B] --results--+--> [Orchestrator] --assemble--> Output
     +--decompose-->                   [Worker C] --results--+
```

**When to use:** Cross-functional workflows with clear task decomposition. Customer service routing, content pipelines, research workflows.

**Production evidence:** Wells Fargo (35,000 bankers access 1,700 procedures in 30 seconds), Salesforce Agentforce 2.0, 40-60% cost reduction by using cheaper models for workers.

**Failure modes:**
- **Context window overflow:** Orchestrator accumulates context from every worker. At 4+ workers, context frequently exceeds window limits.
- **Misclassification compounding:** If orchestrator misclassifies a task, wrong worker gets it; rates compound at scale.

**Mitigations:**
- Summarize/compress worker results before passing to orchestrator
- Implement confidence thresholds for task classification; route low-confidence to human
- Cache decomposition patterns for common task types

### 7.2 Pipeline / Sequential Chain

```
[Agent A] --> [Agent B] --> [Agent C] --> [Agent D]
```

**When to use:** Content creation pipelines (research -> outline -> write -> edit -> fact-check), document processing, ETL workflows.

**Strengths:** Simple to understand, predictable execution, easy to debug.

**Failure modes:**
- Error propagation: An error in Agent A corrupts all downstream work
- Latency accumulation: Each agent adds latency
- No flexibility: Cannot skip steps or branch

**Mitigations:**
- Add validation gates between steps
- Implement rollback to last known good state
- Use conditional edges for lightweight branching

### 7.3 Fan-Out / Fan-In

```
                    +-->[Worker A]--+
[Task]--split------>+-->[Worker B]--+--merge-->[Aggregator]--> Output
                    +-->[Worker C]--+
```

**When to use:** Research tasks, data analysis, batch processing, independent subtask evaluation.

**Production evidence:** Pydantic AI + DBOS deep research; reduces latency from O(n) to O(max(subtask)).

**Failure modes:**
- Synchronization barriers: slowest worker determines total latency
- Merge complexity: combining partial results requires careful context management
- Resource contention: parallel workers compete for GPUs, API rate limits

**Mitigations:**
- Per-worker timeouts
- Streaming result collection
- Rate limit parallel workers

### 7.4 Mixture of Experts (Conditional Routing)

```
[Input]-->[Router Agent]--+--(billing)-->[Billing Expert]
                           +--(technical)-->[Tech Support Expert]
                           +--(sales)-->[Sales Expert]
```

**When to use:** Customer service, domain-specific Q&A, classification tasks with specialist depth.

**Strengths:** Only relevant agent is activated -- reduces compute overhead significantly.

**Failure modes:**
- Router accuracy: if router misclassifies, wrong expert handles query
- Expert overlap: ambiguous queries may fit multiple categories

**Mitigations:**
- Multi-label routing with confidence scores
- Allow experts to escalate to other experts
- Monitor router accuracy and A/B test strategies

### 7.5 Pattern Selection Decision Table

| Your Situation | Recommended Pattern | Max Agents | Key Risk |
|---------------|---------------------|------------|----------|
| Clear task decomposition, cross-functional | Orchestrator-Worker | 4 workers + 1 orchestrator | Context overflow at 4+ workers |
| Fixed sequence of transformations | Pipeline/Sequential | 3-5 agents | Error propagation downstream |
| Independent parallel subtasks | Fan-Out/Fan-In | 4-8 parallel workers | Slowest worker sets latency |
| Domain-routed queries | Mixture of Experts | 1 router + 1 expert | Router misclassification |
| Verification/quality judgment | Collaborative Debate | 3 agents (adaptive termination) | Endless loops without termination |
| Brainstorming/multi-perspective | Peer-to-Peer (structured) | 3-5 agents | Consensus difficulty; O(N^2) messaging |
| Enterprise org-structure workflow | Hierarchical Command | 2-3 levels max | Information loss at each level |
| Complex conditional + durability needed | LangGraph StateGraph | 3-4 nodes per subgraph | Steep learning curve |

---

## 8. Observability and Debugging

### 8.1 Session-Scoped Distributed Tracing

Traditional APM tools fail for agent systems because they assume stateless, deterministic execution. Agent observability requires **session-scoped distributed tracing** that captures multi-turn causal chains.

**Every trace must include:**
- Session ID (correlates all agents in a workflow)
- Parent-child relationships (which agent called which)
- Full input/output for each agent turn
- Tool call parameters and results
- State changes at each checkpoint
- Confidence scores and calibration history
- Error codes and fallback triggers

### 8.2 What to Log at Each Pipeline Phase

| Phase | Required Logs | Optional But Valuable |
|-------|--------------|----------------------|
| Task decomposition | Sub-task list, DAG, allocation decisions, decomposition confidence | Alternative decompositions considered |
| Agent execution | Agent name, model, temperature, full prompt, output, execution time | Token count, cost per call |
| Inter-agent handoff | Source agent, destination agent, payload summary, correlation ID | Context window utilization, compression ratio |
| Verification | Verifier identity, scores per dimension, confidence, reasoning | ACH matrix entries, devil's advocate output |
| Error handling | Error type (MAST code), retry count, fallback used, circuit breaker state | Stack trace equivalent (agent call chain) |
| Assembly | Aggregation method, final output, dissenting opinions | Distribution of individual scores |

### 8.3 Cross-Agent Consistency Checks

```protocol
CONSISTENCY CHECK PROTOCOL:
1. After assembly, run a consistency verifier that checks:
   - Does the output address the original request? (specification compliance)
   - Are facts consistent across agent outputs? (contradiction detection)
   - Does output conform to expected schema? (structural validation)
   - Are confidence scores calibrated? (ECE spot-check)
2. If any check fails, route to human review or retry with modified parameters
3. Log all consistency check results for trend analysis
```

### 8.4 Silent Failure Detection

Silent failures are the most dangerous: everything looks fine, but the system produces subtly wrong results.

**Detection strategies:**
- Output schema validation on all agent outputs (Pydantic models)
- Cross-agent consistency checks on critical outputs
- End-to-end assertions testing the full system, not just individual calls
- Canary deployments: route small % of traffic to new versions; compare outputs
- Eval-gated CI/CD: block deployments if eval scores drop below thresholds

---

## 9. Anti-Patterns

### 9.1 Bag-of-Agents (Unstructured Networks)

**What:** Multiple agents connected in an ad-hoc peer-to-peer network with no governance, no structured messaging, no termination criteria.

**Why it fails:** Amplifies errors up to 17.2x compared to single-agent baselines (SOTA: Kim et al. 2025). Unstructured networks exhibit cascading conformity, endless debate loops, and O(N^2) messaging overhead.

**What to do instead:** Centralized orchestration with structured messaging. Maximum 4 agents per task. Explicit termination criteria.

### 9.2 Intrinsic Self-Correction

**What:** An agent evaluates and attempts to correct its own output without external feedback.

**Why it fails:** Performance often degrades after self-correction attempts (SOTA: Huang et al. ICLR 2024). LLMs generate plausible but internally coherent errors that evade self-detection. Overconfidence (ECE up to 74%) makes agents poor judges of their own work.

**What to do instead:** Route verification to a separate agent with a different model family, or use external tools (unit tests, search, calculator). Use Re-ReST to distill self-correction into the model during training, not at inference time.

### 9.3 Peer-to-Peer Without Governance

**What:** Agents communicate directly without an orchestrator, shared state, or structured protocols.

**Why it fails:** Consensus difficulty (agents disagree indefinitely), communication overhead (O(N^2) paths), emergent behaviors that don't appear in single-agent testing, and peer pressure dynamics that amplify errors (Academic: MAEBE peer pressure rises from 28.5% to 43.9% under misaligned supervisors).

**What to do instead:** Use stigmergy (shared state) as primary coordination. Limit peer-to-peer to structured debate with max 3-5 rounds and adaptive termination.

### 9.4 Orchestrator Doing the Work

**What:** The orchestrator agent performs substantive work instead of just delegating and assembling.

**Why it fails:** Context window overflow as the orchestrator accumulates work from every worker. The orchestrator becomes a bottleneck and single point of failure. Violates separation of concerns.

**What to do instead:** Orchestrator decomposes, delegates, and assembles only. Workers perform all substantive work. Results are summarized before returning to orchestrator.

### 9.5 Reviewers That Never Issue REVISE

**What:** Reviewer agents that always approve outputs or provide only cosmetic feedback, never substantive revision requests.

**Why it fails:** Creates a false sense of quality. Defeats the purpose of adversarial verification. Often caused by prompts that bias toward politeness or consensus.

**What to do instead:** Explicitly instruct reviewers to "find flaws." Require reviewers to state at least one concrete issue or explicitly confirm "no issues found." Track reviewer approval rates; investigate if >90%.

### 9.6 Summary: Anti-Pattern Quick Reference

| Anti-Pattern | Root Cause | Fix | Source Streams |
|-------------|-----------|-----|----------------|
| Bag-of-agents | No governance structure | Centralized orchestration, max 4 agents | SOTA, Academic, Industry |
| Intrinsic self-correction | No external feedback signal | Separate verifier agent; external tools | SOTA, Cognitive |
| P2P without governance | No termination; O(N^2) messaging | Stigmergy + structured debate only | Academic, Industry, SOTA |
| Orchestrator doing work | Context overflow; bottleneck | Delegate all work; summarize results | Industry |
| Reviewers never revise | Poleness bias; prompt failure | "Find flaws" framing; track approval rates | Cognitive, Industry |
| Simple majority vote | Loses nuance; converges wrong | Weighted aggregation; adversarial verification | Cognitive, Academic, SOTA |
| No validation between steps | Error propagation unchecked | Validation gates between every stage | SOTA, Industry |
| Coherence = correctness | Confidence inflation | Independent fact-checking; uncertainty propagation | SOTA, Cognitive |

---

## 10. Integration Cheat Sheet

### 10.1 Situation -> Pattern -> Reference

| Situation | Recommended Pattern | Section Reference |
|-----------|-------------------|-------------------|
| Need to verify output quality | 3 independent evaluators + ITA protocol | 5.1, 4.3 |
| Quality is borderline | Collaborative debate (3 agents, adaptive termination) | 4.1 |
| Need to prevent groupthink | Devil's advocate + Team B analysis | 4.4, 5.3 |
| Errors propagating downstream | Validation gates between every step | 6.2 |
| System crashed mid-workflow | Durable execution with checkpointing | 6.3 |
| Need to scale beyond 4 agents | Hierarchical decomposition into sub-tasks | 3.4 |
| Silent failures suspected | Cross-agent consistency checks + schema validation | 8.3, 8.4 |
| Overconfident evaluators | Calibration tracking; confidence-calibrated routing | 5.4 |
| Need fastest path to working system | Orchestrator-Worker with 3 specialists | 7.1 |
| Processing independent data batches | Fan-Out/Fan-In with timeout per worker | 7.3 |
| Routing by domain | Mixture of Experts with confidence scoring | 7.4 |
| Reviewers always approve | "Find flaws" prompt framing; track approval rates | 9.5 |
| Agents conforming to wrong majority | Independent first-round + anti-conformity guardrails | 5.1, 4.1 |

### 10.2 Decision Flowchart (Text Form)

```
START: New task arrives
|
+-- Is it a simple, well-understood task? --> YES --> Use 1 best agent (2.1)
|   NO
|
+-- Can it be decomposed into independent sub-tasks? --> YES --> Fan-Out/Fan-In (7.3)
|   NO
|
+-- Does it require cross-functional expertise? --> YES --> Orchestrator-Worker (7.1)
|   |   |
|   |   +-- More than 4 workers needed? --> YES --> Hierarchical decomposition (3.4)
|   NO
|
+-- Is it a verification/quality judgment task? --> YES --> Collaborative Debate (4.1)
|   |   |
|   |   +-- High stakes or ambiguous? --> YES --> Add Devil's Advocate (5.3) + ACH (4.4)
|   NO
|
+-- Does it require domain-specific routing? --> YES --> Mixture of Experts (7.4)
|   NO
|
+-- Default: Orchestrator-Worker with 3 specialists, validation gates, durable execution

AFTER OUTPUT GENERATED:
|
+-- Run Independent-Then-Aggregate verification (5.1)
|   +-- Confidence < 0.7 or high disagreement? --> YES --> Structured Debate (4.1)
|   +-- All checks pass? --> YES --> Deliver with confidence metadata
|
+-- Log full trace for trace-to-eval pipeline (6.4)
+-- Run MAST audit checklist before deployment (6.5)
```

### 10.3 Pre-Deployment Checklist

- [ ] Agent count <= 4 per task (or decomposed hierarchy)
- [ ] Diverse model families for evaluators (not all same family)
- [ ] Independent evaluation enforced before aggregation
- [ ] Validation gates between every pipeline stage
- [ ] Durable execution (checkpointing) implemented
- [ ] Circuit breakers on all external calls
- [ ] Structured messaging schemas (not free-form text)
- [ ] Adaptive termination on all debate/iteration loops
- [ ] MAST taxonomy audit completed (14 failure modes checked)
- [ ] Trace-to-eval pipeline configured
- [ ] Cross-agent consistency checks implemented
- [ ] Silent failure detection (schema validation + canary)
- [ ] Calibration tracking for all evaluator agents
- [ ] Context overflow mitigation (summarization at handoffs)
- [ ] Human escalation path for low-confidence outputs

---

## Source Legend

| Stream | Key Sources | Coverage |
|--------|------------|----------|
| **Academic** | CJT generalizations, hierarchical LLM multi-agent (arXiv:2602.21670), MAEBE (arXiv:2506.03053), bandwidth-efficient comm (arXiv:2602.02035), GVQ, PBFT, DAG-based allocation | Collective intelligence, task decomposition, consensus, emergent behavior, communication |
| **Industry** | LangGraph, CrewAI, AutoGen v0.4, OpenAI Swarm/Agents SDK, Beam.ai, Braintrust, Temporal.io, production case studies (Wells Fargo, Salesforce, CyberArk) | Frameworks, production patterns, failure modes, observability, deployment |
| **Cognitive** | JudgeBench, LLM-as-a-Fuser, CONSENSAGENT, Free-MAD, CIA Tradecraft Primer (ACH), Janis groupthink, Bikhchandani information cascades, Diversity Prediction Theorem, superforecaster research, SKAIR framework | Bias mitigation, structured analytics, wisdom of crowds, calibration, feedback |
| **SOTA** | Huang ICLR 2024, Ji EMNLP 2024 (Re-ReST), Cemri NeurIPS 2025 (MAST), Kim 2025 (scaling), multi-agent debate 2025, emergent coordination 2025, error cascade modeling 2026 | LLM-as-judge, self-correction, debate, error propagation, self-organization |

---

*This document synthesizes findings from 100+ sources across academic papers, industry frameworks, cognitive science research, and state-of-the-art evaluations. Every recommendation represents convergent evidence from at least two independent research streams. When evidence conflicts, the stronger empirical evidence prevails.*
