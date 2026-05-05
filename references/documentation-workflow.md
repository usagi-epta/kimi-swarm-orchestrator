# Documentation Workflow

> **Reference for swarm-orchestrator** — loaded when the swarm is producing documentation, technical specs, ADRs, or any structured written content for human consumption.

Guide collaborative document creation through a structured three-stage workflow. Act as an active facilitator: gather context, build sections iteratively, and verify the document works for readers before marking it complete.

## When to Apply

- Co-authoring documentation with users (specs, PRDs, decision docs, RFCs).
- Reviewing docs for completeness, clarity, and consistency.
- Following a documentation lifecycle from draft to publication.

## Trigger Conditions

Offer this workflow when the user mentions:

- Writing documentation: "write a doc", "draft a proposal", "create a spec"
- Specific doc types: "PRD", "design doc", "decision doc", "RFC"
- Starting a substantial writing task

If the user declines, proceed freeform. If accepted, walk through the three stages below.

## Workflow Overview

```
Stage 1: Context Gathering    → Close the gap between user knowledge and agent knowledge
Stage 2: Refinement & Structure → Build section by section through iteration
Stage 3: Reader Testing       → Verify the doc works for fresh readers
```

---

## Stage 1: Context Gathering

**Goal:** Gather enough context that edge cases and trade-offs can be discussed without needing basics explained.

### Initial Questions

Ask the user for meta-context about the document:

| # | Question |
|---|---|
| 1 | What type of document is this? (spec, decision doc, proposal, etc.) |
| 2 | Who is the primary audience? |
| 3 | What is the desired impact when someone reads this? |
| 4 | Is there a template or specific format to follow? |
| 5 | Any constraints or additional context to know? |

Inform the user they can answer in shorthand or dump information however works best.

### Template Handling

- If a template is provided: read it and ask if the structure should be followed exactly.
- If editing an existing shared document: read the current state, check for images without alt-text, and offer alt-text generation.

### Info Dumping

Encourage the user to dump all context without worrying about organization:

- Background on the project/problem
- Related discussions or shared documents
- Why alternative solutions were rejected
- Organizational context (team dynamics, past incidents)
- Timeline pressures or constraints
- Technical architecture or dependencies
- Stakeholder concerns

As context is provided, track what is learned and what remains unclear.

### Clarifying Questions

Once the initial dump is complete, generate 5-10 numbered questions targeting gaps in understanding. Accept shorthand answers, links to docs, or pointers to channels.

**Exit condition:** Sufficient context exists when questions demonstrate understanding — edge cases and trade-offs can be discussed without revisiting basics.

---

## Stage 2: Refinement & Structure

**Goal:** Build the document section by section through brainstorming, curation, and iterative refinement.

### Section Ordering

- If structure is clear: ask which section to start with. Recommend starting with the section that has the most unknowns (usually the core proposal/approach).
- If structure is unknown: suggest 3-5 sections appropriate for the doc type and ask for approval.

### Scaffold Creation

Create the initial document structure with placeholder text:

```markdown
# Document Title

## Section 1
[To be written]

## Section 2
[Content here]
```

### Per-Section Workflow

For each section, follow these steps:

| Step | Action |
|---|---|
| 1. Clarifying questions | Ask 5-10 specific questions about what this section should cover |
| 2. Brainstorming | Generate 5-20 numbered options of what might be included |
| 3. Curation | Ask user which to keep/remove/combine; accept freeform feedback |
| 4. Gap check | Ask if anything important is missing from the selected items |
| 5. Drafting | Write the section, replacing placeholder text |
| 6. Iterative refinement | Apply surgical edits based on feedback; never reprint the whole doc |

### Iteration Guidance

- Use `str_replace` for all edits — never reprint the entire document.
- Continue iterating until the user is satisfied with the section.
- After 3 consecutive iterations with no substantial changes, ask if anything can be removed without losing important information.
- Confirm the section is complete before moving to the next.

### Near Completion

When 80%+ of sections are drafted:

1. Re-read the entire document for flow and consistency across sections.
2. Check for redundancy, contradictions, generic filler, or sentences that carry no weight.
3. Provide any final suggestions before proceeding to Reader Testing.

---

## Stage 3: Reader Testing

**Goal:** Test the document with a fresh agent instance (no context bleed) to verify it works for readers.

### Step 1: Predict Reader Questions

Generate 5-10 realistic questions readers would ask when encountering this document for the first time.

### Step 2: Test with Fresh Agent

If sub-agents are available:
- Invoke a fresh agent with only the document content and one question per call.
- Summarize what the reader agent got right and wrong.

If no sub-agents:
- Provide the user with testing instructions: open a fresh conversation, paste the document, and ask the predicted questions.

### Step 3: Additional Checks

Ask the reader agent or user to verify:

- What in the doc might be ambiguous or unclear?
- What knowledge does the doc assume readers already have?
- Are there internal contradictions or inconsistencies?

### Step 4: Report and Fix

If issues are found:

1. List the specific gaps or misinterpretations.
2. Loop back to Stage 2 refinement for problematic sections.
3. Re-test after fixes.

**Exit condition:** The doc is ready when a fresh reader consistently answers questions correctly and surfaces no new gaps.

---

## Final Review

When Reader Testing passes:

1. Recommend the user do a final read-through — they own the document and are responsible for its quality.
2. Ask them to double-check facts, links, and technical details.
3. Ask them to verify it achieves the impact they wanted.

Provide final tips:

- Consider linking the collaboration thread in an appendix.
- Use appendices to provide depth without bloating the main doc.
- Update the doc as feedback is received from real readers.

---

## Review Checklists

### Before Reader Testing

- [ ] Every section has substantive content (no placeholders remain).
- [ ] Technical claims have supporting evidence or references.
- [ ] Terms are defined on first use.
- [ ] Decision rationale is explicit (not just the decision).
- [ ] No contradictions between sections.

### Before Publication

- [ ] Reader Testing passed (fresh reader understood the doc).
- [ ] All links verified.
- [ ] Code examples tested or marked as illustrative.
- [ ] Audience-appropriate (level and terminology match target readers).

---

## Tips for Effective Guidance

| Concern | Guidance |
|---|---|
| Tone | Be direct and procedural; explain rationale only when it affects behavior |
| Skipping stages | Ask if the user wants to skip and work freeform instead |
| Frustration | Acknowledge the pace; suggest ways to move faster |
| Context gaps | Address gaps as they arise; do not let them accumulate |
| Quality vs. speed | Each iteration should make meaningful improvements |
