# Anti-Bias Protocols for Swarm Arbitration

## Table of Contents

- [Introduction](#introduction)
- [The Six Bias Categories](#the-six-bias-categories)
  - [Halo Effect](#a-halo-effect)
  - [Warmth Bias](#b-warmth-bias)
  - [Primacy Bias](#c-primacy-bias)
  - [Recency Bias](#d-recency-bias)
  - [Inter-Agent Anchor Contamination](#e-inter-agent-anchor-contamination)
  - [Contrast Effects](#f-contrast-effects)
- [The Evaluation Protocol](#the-evaluation-protocol)
- [Scoring Dimensions](#scoring-dimensions)
- [Warmth Suppression Rule](#warmth-suppression-rule)
- [Finality Protocol](#finality-protocol)
- [Prohibited Behaviours](#prohibited-behaviours)
- [Self-Diagnostic Checklist](#self-diagnostic-checklist)

---

## Introduction

An orchestrator arbitrating between multiple agent outputs is a judge with no stake in the outcome. The moment that neutrality is compromised, the swarm produces suboptimal results — not through agent failure, but through orchestrator error.

**Core principle**: A comparator with preference produces noise. A comparator without stake produces clean signal.

Bias in swarm arbitration is not a character flaw; it is a predictable cognitive response to repeated evaluation tasks. This document specifies protocols that neutralise six documented bias categories. It supplements the `executor + evaluator pairing` pattern described in `references/swarm-patterns.md` — evaluation is only as clean as the arbitration that governs it.

These protocols are grounded in empirical findings on human judgment and decision-making. They apply whether the orchestrator is comparing two outputs or twenty.

---

## The Six Bias Categories

Each bias is described with its mechanism, mitigation, and detection signal. Detection signals are phrases or patterns that should trigger immediate protocol review.

### a. Halo Effect

**Definition**: A strong performance on one evaluation dimension inflates scores on unrelated dimensions.

**Empirical basis**: Judges who observe higher ability on one dimension predictably produce inflated scores on separate, unrelated dimensions. The correlation between dimensions in judged data exceeds the correlation in objective performance (Belle et al., 2017).

**Mechanism in swarm arbitration**: Agent A produces an output with excellent structure. The orchestrator, impressed by the structure, also scores it higher on accuracy and relevance — even when the content contains errors or off-topic material.

**Mitigation — Dimension-crossing evaluation**:

| Instead of... | Do this... |
|---------------|------------|
| Score all dimensions for Agent A, then all for Agent B | Score all agents on Coherence first. Then all agents on Relevance. Then all on Alignment. |

Complete every agent on dimension X before touching dimension Y. This breaks the halo pathway by forcing the evaluator to context-switch between dimensions.

**Detection signal**: Any statement of the form *"This output is great overall"* without per-dimension justification. Overall greatness is a halo symptom, not a valid observation.

**Example — biased vs. unbiased**:

| Biased (Halo) | Unbiased (Dimension-Crossing) |
|---------------|-------------------------------|
| Agent A: Coherence 9, Relevance 9, Alignment 9 — "the structure is excellent so the rest follows" | Agent A: Coherence 9, Relevance 6, Alignment 7 — "structure is strong; however, two paragraphs do not address the mission; role constraints partially ignored" |
| Agent B: Coherence 6, Relevance 6, Alignment 6 — "doesn't have the polish of Agent A" | Agent B: Coherence 6, Relevance 8, Alignment 8 — "messy structure but every paragraph addresses the mission; role constraints fully satisfied" |

---

### b. Warmth Bias

**Definition**: A favourable subjective feeling toward an output is treated as evidence of its quality.

**Mechanism**: One output will feel more comfortable, familiar, or aligned with the orchestrator's own style or preferences. This warmth is a neurological response, not a quality indicator. It masquerades as judgment because it produces confidence — the evaluator *feels* certain.

**Mitigation**: Score against explicit criteria, not comfort. If an output feels good, that feeling is data about the evaluator, not about the output. Note the warmth and disregard it.

**Detection signal**: Any scoring reason of the form *"I really like how this one flows"*, *"This feels right"*, *"This resonates better"*. Liking is not a criterion. Flow is not a dimension.

**What warmth looks like in practice**:

| Warmth Indicator | What to Do |
|------------------|------------|
| "I find this more convincing" | Identify the specific evidence or reasoning that produced conviction. If you cannot name it, the warmth is ungrounded. |
| "This aligns with how I would approach it" | Disregard. The orchestrator's approach is irrelevant. |
| "The tone here is better" | Check if tone is in the scoring rubric. If not, it is not a scoring input. |

---

### c. Primacy Bias

**Definition**: The first output reviewed receives systematically elevated scores.

**Empirical basis**: First-encountered information receives disproportionate weight in subsequent judgments (Fourakis et al., 2020). The initial output sets a psychological baseline against which later outputs are implicitly measured.

**Mechanism in swarm arbitration**: The orchestrator reads Agent A's output first. It establishes the mental model of what "this task looks like." Agent B's output is then evaluated as a deviation from that model — deviations score lower even when they are improvements.

**Mitigation — Exposure before assessment**:

1. Read all outputs from start to finish.
2. While reading, do not evaluate. Read to understand, not to assess.
3. Only after all outputs have been read begin scoring.

**Detection signal**: Consistently higher scores for the first agent reviewed across multiple evaluation rounds. If Agent A is first and scores highest, check the order.

| Biased Order | Unbiased Order |
|--------------|----------------|
| Read A → score A → read B → score B → read C → score C | Read A, B, C (exposure only) → pause → score all on Coherence → score all on Relevance → score all on Alignment |

---

### d. Recency Bias

**Definition**: The most recently read or evaluated output receives disproportionate weight.

**Mechanism**: Compounds with primacy bias. When evaluation immediately follows reading, the last-read output is most accessible in working memory. This accessibility is mistaken for quality — the output feels more detailed, more complete, simply because it is more available.

**Mitigation — Interrupt the recency pathway**:

1. After reading all outputs, pause before scoring.
2. Do not score the last-read output first.
3. If possible, begin scoring with a middle agent, not the first or last read.

**Detection signal**: Higher scores for the most recently reviewed agent. If the agent reviewed just before scoring consistently outperforms, recency bias is active.

| Reading Order | Scoring Order (to counter recency) |
|---------------|-----------------------------------|
| A → B → C | Begin with B, then A, then C |

---

### e. Inter-Agent Anchor Contamination

**Definition**: One strong output sets an implicit reference point against which all others are compared.

**Empirical basis**: Sequential evaluators compare each new option to those that preceded them, producing systematically different scores than judges who evaluate options independently (De Bruin & Keren, 2003).

**Mechanism in swarm arbitration**: Agent A produces an exceptional output. Agent B's output is then scored not against the rubric, but against Agent A — *"Not as strong as A on structure"* becomes a 6 instead of a 7, even if a 7 is rubric-justified. Agent C's output benefits from contrast with B and scores higher than B, again not against the rubric.

**Mitigation — Absolute criteria anchoring**:

Each score answers only: **"How well does this output satisfy the criterion in absolute terms?"** Not "How does this compare to Agent A?" Not "Is this better than the last one?"

**Detection signal**: Any comparative language in scoring justification — *"Compared to Agent A's output, this one is..."*, *"Not as thorough as B"*, *"Better structured than C"*. Comparisons between agents indicate anchor contamination.

| Contaminated Scoring | Clean Scoring |
|----------------------|---------------|
| "Agent B gets a 6 on Coherence — not as tight as Agent A's 9" | "Agent B gets a 7 on Coherence — logical flow is present throughout; minor structural inconsistency in section 3 prevents an 8" |

---

### f. Contrast Effects

**Definition**: A weak output gets dragged down because it followed a strong one; a strong output gets inflated because it followed a weak one.

**Mechanism**: Relative positioning distorts absolute evaluation. The same output receives different scores depending on what the evaluator saw immediately before it. This is distinct from anchor contamination (which uses a single strong reference point) — contrast effects are directional, sequence-dependent distortions.

**Mitigation**: Score against absolute criteria. If scores cluster at extremes (very high and very low) without middle values, contrast effects are likely operating. A healthy score distribution includes middle values — most outputs are imperfect but not failures.

**Detection signal**: Scores cluster at the extremes (9s and 3s, no 6s). When outputs that should be middling are instead polarised, contrast effects are active.

| Contrast-Distorted Distribution | Healthy Distribution |
|--------------------------------|----------------------|
| Agent A: 9, Agent B: 3, Agent C: 9 | Agent A: 7, Agent B: 5, Agent C: 8 |
| (Extreme clustering — no middle ground) | (Middle values present — nuanced differentiation) |

---

## The Evaluation Protocol

Follow these steps in sequence for every arbitration.

| Step | Action | Bias Prevented | What Not to Do |
|------|--------|----------------|----------------|
| **0 — Exposure** | Read all outputs with no evaluative intention. Read to understand, not to assess. | Primacy, Recency | Do not score while reading. Do not mentally rank. |
| **1 — Pause** | Interrupt between reading and scoring. Explicitly pause. | Recency | Do not begin scoring immediately after reading the last output. |
| **2 — Dimension Crossing** | Score all agents on dimension X before touching dimension Y. | Halo | Do not complete all dimensions for one agent before moving to the next. |
| **3 — Absolute Criteria** | Score against explicit criteria, not against other agents' outputs. | Anchor contamination, Contrast | Do not use comparative language in scoring justification. |
| **4 — Forced Justification** | Justify each score before writing it. If you cannot justify the score with evidence from the output, do not write it. | Warmth, Halo | Do not write a score and then invent justification. |
| **5 — Score Lock** | Do not revise earlier scores based on later ones. Scores are locked once written. | Contrast, Recency | Do not go back and adjust Agent A's score after scoring Agent B. |

### Step 0 Detail: Exposure Without Anchoring

Exposure means reading every output from beginning to end without forming evaluations. This is harder than it sounds. The mind wants to assess — to label, rank, and judge. Suppress this impulse.

**Permitted during exposure**: Note-taking on content (what is said, what evidence is used, what structure is followed).
**Prohibited during exposure**: Evaluative notes ("this is good", "this is weak", "better than the first one").

### Step 5 Detail: Score Lock Rationale

Score revision is the primary pathway for contrast contamination. The orchestrator scores Agent A, then scores Agent B higher or lower, and returns to "adjust" Agent A. That adjustment is not correction — it is contrast poisoning the earlier judgment. The first score was made with cleaner information than the revised score.

**Exception**: If new factual information emerges that was not available during the first scoring (e.g., Agent B's output reveals Agent A contains a factual error), note the error separately. Do not change the original dimension score. The factual error belongs in a correction workflow, not a score revision.

---

## Scoring Dimensions

Evaluate every agent output on these three dimensions. Each dimension scores 0–10 with the anchors below.

### Coherence (0–10)

Internal consistency, logical flow, and absence of contradictions. Does the output hold together as a reasoning structure?

| Score | Anchor | Description |
|-------|--------|-------------|
| **0** | Incoherent | Output is self-contradictory or nonsensical. No logical thread can be identified. |
| **5** | Structurally Sound | Logical thread is present. Minor gaps or weak transitions exist but do not prevent comprehension. |
| **10** | Seamless | Every section connects to the next. Arguments build on each other. No contradictions anywhere. |

**What Coherence is NOT**: Eloquence, style, polish, or grammatical perfection. A dry, plain-spoken output can score 10 on Coherence. A beautifully written output with a logical gap can score 5.

### Relevance (0–10)

Direct alignment with the mission. No padding, no tangents, complete coverage of requirements.

| Score | Anchor | Description |
|-------|--------|-------------|
| **0** | Off-mission | Output does not address the assigned task. Entirely off-topic or produced for a different mission. |
| **5** | Partially Relevant | Core mission addressed. Some required elements present. Contains padding or minor tangents. |
| **10** | Precisely Targeted | Every element directly serves the mission. No padding. All requirements addressed. |

**What Relevance is NOT**: Thoroughness beyond scope. Padding a response with tangentially related material to appear comprehensive reduces Relevance. Completeness within scope is the target.

### Alignment (0–10)

Conformance to the assigned role, constraints, and stylistic/format requirements for that specific agent.

| Score | Anchor | Description |
|-------|--------|-------------|
| **0** | Misaligned | Output violates explicit constraints or role definition. Wrong format, wrong voice, wrong scope. |
| **5** | Mostly Aligned | Role and constraints largely satisfied. Minor deviations from format or voice requirements. |
| **10** | Fully Aligned | Every constraint satisfied. Voice, format, scope, and depth match the agent specification exactly. |

**What Alignment is NOT**: General quality. An output can be excellent in absolute terms but misaligned if it does not conform to the specific constraints assigned to that agent.

### Scoring Worksheet Template

Use this structure to enforce dimension-crossing:

```
=== COHERENCE ===
Agent A: [0-10] — [justification with evidence]
Agent B: [0-10] — [justification with evidence]
Agent C: [0-10] — [justification with evidence]

=== RELEVANCE ===
Agent A: [0-10] — [justification with evidence]
Agent B: [0-10] — [justification with evidence]
Agent C: [0-10] — [justification with evidence]

=== ALIGNMENT ===
Agent A: [0-10] — [justification with evidence]
Agent B: [0-10] — [justification with evidence]
Agent C: [0-10] — [justification with evidence]
```

---

## Warmth Suppression Rule

### The Specific Risk

In every multi-agent evaluation, one output will likely feel more comfortable — more familiar in style, more aligned with the orchestrator's own patterns of thought, easier to read. This is the warmth response. It is predictable, automatic, and dangerous to evaluation accuracy.

### The Rule

**Favourable feeling is not evidence of quality.**

Warmth is data about the evaluator, not the output. It signals alignment between the output's style and the evaluator's preferences. The evaluation protocol exists precisely because preferences must not enter scoring.

### The Mechanism

Neutral, detached evaluators produce less halo contamination and greater scoring accuracy than engaged, preference-expressing evaluators. Warmth opens the door to halo — the evaluator who likes one aspect of an output extends that liking to unrelated dimensions.

### Implementation

When warmth is detected during scoring:

1. **Acknowledge**: Note that warmth is present. Name it explicitly: *"I notice I prefer this output's style."*
2. **Quarantine**: Set the warmth aside. Do not use it as scoring input.
3. **Re-score**: Return to Step 2 of the Evaluation Protocol. Re-score the dimension against criteria alone.
4. **Verify**: If the re-score differs from the original, the warmth was distorting the score. The re-score stands.

| Warmth Present | Correct Response |
|----------------|------------------|
| "This output feels more professional" | Check if "professional" is a scoring criterion. If not, disregard. |
| "I connect with this reasoning style" | Identify specific reasoning steps. Score those steps against criteria. |
| "This one is more persuasive" | Identify the evidence and argument structure that produced persuasion. Score those. |

---

## Finality Protocol

Arbitration produces clear rulings. Ambiguity in the final ruling is a failure of the orchestrator, not a kindness to agents.

### Permitted Rulings

| Ruling Type | Example |
|-------------|---------|
| Pass with dimension note | "Agent A's output passes. Coherence: 8, Relevance: 9, Alignment: 9." |
| Fail with dimension specificity | "Agent B's output fails on Relevance (4/10) — sections 2 and 3 do not address the mission requirements. Coherence and Alignment are acceptable (7 and 6 respectively)." |
| Selective pass | "Agent A passes on all dimensions. Agent B fails on Alignment (3/10) — output violates the format constraint specified in the mission." |

### Prohibited Rulings

| Ruling Type | Example | Why Prohibited |
|-------------|---------|----------------|
| Hedged finality | "Both showed strengths in different areas" | No actionable outcome. Fails the arbitration function. |
| Conditional pass | "It depends on whether you value structure over content" | The orchestrator decides. Conditions belong in the orchestrator's judgment, not the ruling. |
| Blended assessment | "Agent A was stronger on coherence, Agent B on relevance" | Without a final selection or pass/fail, this is description, not arbitration. |
| Equivocation | "Both performed well, honestly" | "Both performed well" is not a valid ruling. Specify which passes and which fails, and on what dimensions. |

### Where Qualifications Belong

Per-dimension notes are the correct place for nuance:

- **Final ruling**: Clear pass/fail or selection.
- **Per-dimension notes**: "Scored 7 on Coherence — strong structure but one logical gap in section 4 prevents a higher score."

Nuance enriches dimension notes. Nuance corrupts final rulings.

---

## Prohibited Behaviours

The following behaviours are prohibited during arbitration. Each entry includes the bias pathway it activates and the protocol step that prevents it.

| Behaviour | Bias Activated | Prevention Protocol | Why Prohibited |
|-----------|---------------|---------------------|----------------|
| Advocating for an agent mid-evaluation | Warmth, Halo | Detachment stance — no stake in any agent's success | The orchestrator is not an agent's ally. Advocacy collapses the distinction between orchestrator and agent. |
| Revising a locked dimension's scores | Contrast, Recency | Step 5: Score Lock | Revisions after seeing later scores are contaminated by contrast, not improved by information. |
| Softening rulings with qualifications | N/A — procedural failure | Finality Protocol | Softened rulings fail the user. The orchestrator's job is to decide, not to hedge. |
| Drifting toward the agent whose style matches the orchestrator | Warmth | Warmth Suppression Rule | Style matching is a warmth signal, not a quality signal. |
| Treating auto-metrics as ground truth rather than signals | N/A — category error | Step 4: Forced Justification | Metrics (token count, reading ease, etc.) are inputs to judgment, not replacements for it. |
| Scoring one agent relative to another at per-dimension level | Anchor contamination, Contrast | Step 3: Absolute Criteria | Per-dimension comparison activates anchor contamination. Each score stands alone against the rubric. |
| Scoring immediately after reading without pausing | Recency | Step 1: Pause | Immediate scoring inflates the last-read output due to working memory accessibility. |
| Scoring all dimensions for one agent before moving to the next | Halo | Step 2: Dimension Crossing | Completing all dimensions per agent allows strong performance on one dimension to inflate others. |
| Reading outputs evaluatively (ranking while reading) | Primacy | Step 0: Exposure Without Anchoring | Evaluative reading establishes anchors that distort subsequent judgment. |
| Failing to justify a score before writing it | Warmth, Halo | Step 4: Forced Justification | Unjustified scores are post-hoc rationalisations of feeling, not evidence-based assessments. |

---

## Self-Diagnostic Checklist

Ask these questions before finalising any ruling. A "no" to any question is a signal to pause and re-evaluate.

| # | Question | If No... | If Yes... |
|---|----------|----------|-----------|
| 1 | Have I read **ALL** outputs before scoring **ANY**? | Restart at Step 0. Read remaining outputs without evaluating. | Proceed. |
| 2 | Did I pause between reading and scoring? | Pause now. Do not score immediately after reading. | Proceed. |
| 3 | Did I score by dimension across agents (not all dimensions per agent)? | Re-score using dimension-crossing order. | Proceed. |
| 4 | Can I justify each score with **specific evidence** from the output? | Revisit the score. If no evidence exists, the score is warmth-driven. | Proceed. |
| 5 | Have I revised any earlier scores based on later ones? | Undo the revision. The original score was made with cleaner information. | Proceed. |
| 6 | Am I scoring any agent **relative to another** (e.g., "better than Agent A")? | Re-score against absolute criteria. Comparisons are prohibited. | Proceed. |
| 7 | Is warmth influencing any score — does one output feel better without evidence? | Return to Step 2. Re-score the affected dimension. | Proceed. |
| 8 | Does my final ruling specify pass/fail with dimension-level evidence? | Sharpen the ruling. Remove hedging. Specify which agent, which dimension, what evidence. | Finalise. |

### Escalation Rule

If three or more checklist answers are "no," abort the current evaluation. Restart from Step 0 with fresh exposure. A heavily compromised evaluation cannot be salvaged by partial correction — the contamination is already too deep.

---

## References

- Belle, N., Cantarelli, P., & Belardinelli, P. (2017). Cognitive biases in performance appraisal. *Public Performance & Management Review*, 40(4), 1–24.
- De Bruin, W. B., & Keren, G. (2003). Inspection traps or size-effect? A re-examination of prospect theory. *Journal of Behavioral Decision Making*, 16, 283–301.
- Fourakis, E. M., Margolin, D. I., & Wright, H. H. (2020). Primacy and recency effects in nonword repetition. *Journal of Speech, Language, and Hearing Research*, 63(8), 2595–2603.

## Related Files

- `SKILL.md` — Core orchestration skill, arbitration stance, and pipeline phases
- `references/swarm-patterns.md` — Orchestration patterns including executor + evaluator pairing
- `references/quality-gates.md` — Binary gate framework for validation
