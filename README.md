# Kimi Swarm Orchestrator

> *Orchestrate and manage multi-agent swarms for complex, real-world tasks.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

The Kimi Swarm Orchestrator is a structured framework for decomposing complex requests into interdependent subtasks, dispatching them to specialized sub-agents, validating outputs with binary quality gates, and integrating the results into a single coherent deliverable. It is designed for tasks that require parallel execution, multi-stage workflows, coordination, or quality arbitration—not for single-agent, one-step requests.

---

## ✨ Features

- **7‑Phase Orchestration Pipeline** – Problem restatement, task decomposition, skill discovery, agent creation, dispatch, quality validation, and integration.
- **Structured Decomposition Patterns** – Sequential pipelines, parallel fan‑out, stage‑gated workflows, executor+evaluator pairs, iterative refinement, and more.
- **Anti‑Bias Arbitration Protocols** – Dimensional‑crossing evaluation, warmth‑bias protection, primacy/recency safeguards, and collaborative three‑agent debate for high‑stakes decisions.
- **Binary Quality Gates** – Every output is judged against four dimensions (completeness, correctness, format compliance, integration readiness) with a strict PASS/FAIL ruling—no partial credit.
- **Validator Script** – `validate_swarm_output.py` automates the gate checks and can produce structured JSON or Markdown reports.
- **Plan Generator** – `swarm_plan_generator.py` converts natural‑language task descriptions into structured swarm execution plans (JSON or Markdown).
- **Research‑Backed Swarm Sizing** – Coordination gains plateau beyond 4 agents; the orchestrator enforces optimal swarm sizes (2–4, hard ceiling 6) based on empirical findings.
- **Comprehensive Reference Library** – In‑depth guides on swarm patterns, anti‑bias protocols, quality gates, skill manifests, swarm management, security, system design, documentation workflows, and project context ingestion.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or later
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/usagi-epta/kimi-swarm-orchestrator.git
cd kimi-swarm-orchestrator
```

No additional dependencies are required—the scripts use only the Python standard library.

#### Generate a Swarm Plan

```bash
python scripts/swarm_plan_generator.py "Research AI market trends and write a report" \
  --format markdown --output plan.md
```

The script analyses the task description, identifies stages and dependencies, and recommends agent types.

#### Validate Swarm Output

```bash
python scripts/validate_swarm_output.py output.md \
  --completeness --format-compliance --integration-readiness --correctness \
  --report report.json
```

You can also supply custom criteria via a JSON file:

```bash
python scripts/validate_swarm_output.py output.md --criteria criteria.json
```

---

## 📂 Repository Structure

```
├── LICENSE                # MIT License
├── SKILL.md               # Core skill definition and orchestration pipeline
├── scripts/
│   ├── swarm_plan_generator.py   # Generates structured swarm execution plans
│   └── validate_swarm_output.py  # Validates swarm outputs against quality gates
└── references/
    ├── swarm-patterns.md              # Composable orchestration patterns
    ├── anti-bias-protocols.md         # Bias mitigation for output evaluation
    ├── quality-gates.md               # Binary gate framework and retry logic
    ├── skill-library-manifest.md      # Index of available skills and loading patterns
    ├── swarm-agentic-management.md    # Research‑validated swarm sizing & coordination
    ├── system-design-patterns.md      # Domain decomposition and API design
    ├── security-comprehensive.md      # Security audit guide for AI‑generated code
    ├── documentation-workflow.md      # Three‑stage documentation workflow
    └── project-context-ingestion.md   # How to ingest and understand existing codebases
```

---

## 🧠 The Orchestration Pipeline

The orchestrator follows a mandatory 7‑phase pipeline for every complex task:

Phase Purpose Key Action
1. Problem Restatement Parse and formalise the request without decomposition Restate, identify constraints, flag ambiguities
2. Task Decomposition Break into minimal dependent subtasks Create plan.md with stages and dependencies
3. Skill Discovery Identify which skills/scripts the swarm needs Match subtasks to skills in the manifest
4. Agent Creation Create specialised sub‑agents create_subagent with role‑specific prompts
5. Dispatch Execute subtasks in parallel or sequentially Follow dispatch patterns (fan‑out, stage‑gated, etc.)
6. Quality Validation Evaluate outputs against binary gates PASS/FAIL per gate; fix or escalate on failure
7. Integration Merge validated outputs into a final deliverable Synthesise, format, and deliver

---

## ⚖️ Quality Gates & Arbitration

· Four Dimensions: Completeness, Correctness, Format Compliance, Integration Readiness.
· Binary Ruling: Each gate is PASS or FAIL. No “mostly passes.”
· Failure Handling: On FAIL, dispatch a fix agent with a detailed brief. Escalate after three failures.
· High‑Stakes Protocol: Three evaluators with independent first‑round scoring followed by collaborative debate.
· Anti‑Bias Protections: Dimensional‑crossing evaluation, warmth‑bias detection, primacy/recency safeguards, and information‑cascade prevention.

---

## 🔧 Scripts

`swarm_plan_generator.py`

Generates a structured swarm execution plan from a natural‑language task description. Outputs JSON for programmatic use or Markdown for human review.

`validate_swarm_output.py`

Validates swarm‑generated output files against explicit criteria. Supports custom criteria, hard/soft gate configuration, retry recommendations, and structured reporting.

---

## 📚 Reference Library

All reference documents are loaded progressively during orchestration—never all at once.

| Document                     | Purpose                                                                       |
| ---------------------------- | ----------------------------------------------------------------------------- |
| swarm-patterns.md            | Composable patterns: sequential, parallel, stage‑gated, fan‑out/fan‑in, etc.  |
| anti-bias-protocols.md       | Six documented bias categories with mitigation strategies.                    |
| quality-gates.md             | Binary gate framework, validation dimensions, retry logic, escalation.        |
| skill-library-manifest.md    | Index of available skills, trigger conditions, and loading patterns.          |
| swarm-agentic-management.md  | Research‑backed guidance on swarm sizing, coordination, and error management. |
| system-design-patterns.md    | Domain decomposition, API design, consistency planning.                       |
| security-comprehensive.md    | Full security audit guide for AI‑generated code.                              |
| documentation-workflow.md    | Three‑stage workflow for co‑authoring documentation.                          |
| project-context-ingestion.md | How to build a mental model of an existing codebase.                          |

---

## 🤝 Contributing

Contributions are welcome! This repository follows a structured approach to swarm orchestration—please ensure any new patterns, scripts, or references align with the principles outlined in SKILL.md.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Submit a pull request with a clear description of the change and its motivation.

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

---
## Acknowledgements

This skill was developed and built with assistance from [Kimi](https://kimi.moonshot.cn), using the **skill-creator-swarm** built-in agent framework for multi-agent orchestration and skill packaging framework.

---

> “*A comparator without stake produces clean signal. A comparator with preference produces noise.*”
