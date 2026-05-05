#!/usr/bin/env python3
"""
Swarm Plan Generator

Generates structured swarm execution plans from natural language task descriptions.
Identifies stages, dependencies, parallelization opportunities, and recommends
agent types for each stage. Outputs JSON (programmatic) or Markdown (human review).

Usage:
    python swarm_plan_generator.py "Research AI market trends and write a report" \\
        --format markdown --output plan.md
    python swarm_plan_generator.py --task-file task.txt --format json --max-agents 5
    echo "Build a REST API" | python swarm_plan_generator.py --format json
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import textwrap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("swarm_plan_generator")

# ---------------------------------------------------------------------------
# Constants / Knowledge Base
# ---------------------------------------------------------------------------

STAGE_KEYWORDS: dict[str, list[str]] = {
    "research": [
        "research", "investigate", "explore", "study", "find", "gather",
        "survey", "analyze data", "collect", "discover", "look up",
    ],
    "analysis": [
        "analyze", "evaluate", "assess", "compare", "benchmark",
        "synthesize", "interpret", "derive insights", "model",
    ],
    "design": [
        "design", "architect", "plan structure", "outline", "spec",
        "blueprint", "wireframe", "prototype", "schema",
    ],
    "implementation": [
        "implement", "build", "develop", "code", "write", "create",
        "construct", "program", "script", "deploy", "configure",
    ],
    "testing": [
        "test", "validate", "verify", "check", "debug", "review",
        "audit", " QA", "quality assurance", "unit test",
    ],
    "documentation": [
        "document", "write report", "README", "manual", "guide",
        "explain", "summarize", "describe", "documenting",
    ],
    "integration": [
        "integrate", "connect", "merge", "combine", "interface",
        "hook up", "link", "pipeline", "CI/CD",
    ],
    "deployment": [
        "deploy", "release", "publish", "ship", "launch", "go live",
        "roll out", "distribute",
    ],
    "review": [
        "review", "proofread", "edit", "refine", "polish",
        "finalize", "approve", "sign off",
    ],
}

AGENT_CATALOG: dict[str, dict[str, Any]] = {
    "researcher-market": {
        "skills": ["deep-research-swarm"],
        "stage_hint": ["research"],
        "description": "Market and industry research specialist",
    },
    "researcher-tech": {
        "skills": ["deep-research-swarm", "code-analysis"],
        "stage_hint": ["research", "analysis"],
        "description": "Technical research and deep-dive specialist",
    },
    "analyst-data": {
        "skills": ["data-analysis", "visualization"],
        "stage_hint": ["analysis"],
        "description": "Data analysis and insight extraction",
    },
    "designer-architect": {
        "skills": ["system-design", "architecture-review"],
        "stage_hint": ["design"],
        "description": "System architecture and design planning",
    },
    "developer-frontend": {
        "skills": ["web-dev", "ui-implementation"],
        "stage_hint": ["implementation"],
        "description": "Frontend development specialist",
    },
    "developer-backend": {
        "skills": ["api-dev", "database-design", "backend-systems"],
        "stage_hint": ["implementation"],
        "description": "Backend and API development specialist",
    },
    "developer-fullstack": {
        "skills": ["web-dev", "api-dev", "deployment"],
        "stage_hint": ["implementation"],
        "description": "Full-stack development generalist",
    },
    "writer-technical": {
        "skills": ["tech-writing", "documentation"],
        "stage_hint": ["documentation"],
        "description": "Technical writing and documentation",
    },
    "writer-reporter": {
        "skills": ["report-writing", "summarization"],
        "stage_hint": ["documentation", "review"],
        "description": "Report authoring and summarization",
    },
    "tester-qa": {
        "skills": ["test-automation", "manual-qa"],
        "stage_hint": ["testing"],
        "description": "Quality assurance and testing",
    },
    "devops-engineer": {
        "skills": ["ci-cd", "infrastructure", "deployment"],
        "stage_hint": ["deployment", "integration"],
        "description": "DevOps and deployment automation",
    },
    "security-auditor": {
        "skills": ["security-review", "penetration-testing"],
        "stage_hint": ["testing", "review"],
        "description": "Security review and audit",
    },
    "editor-chief": {
        "skills": ["editing", "content-review"],
        "stage_hint": ["review"],
        "description": "Editorial review and final approval",
    },
}

STAGE_ORDER_DEFAULT: list[str] = [
    "research",
    "analysis",
    "design",
    "implementation",
    "testing",
    "integration",
    "documentation",
    "review",
    "deployment",
]

STAGE_OUTPUTS: dict[str, list[str]] = {
    "research": ["research_brief.md", "source_list.md"],
    "analysis": ["analysis_report.md", "insights.md"],
    "design": ["design_spec.md", "architecture_diagram.md"],
    "implementation": ["source_code", "build_artifacts"],
    "testing": ["test_report.md", "coverage_report.md"],
    "integration": ["integration_report.md"],
    "documentation": ["README.md", "user_guide.md"],
    "review": ["review_notes.md", "approval_signoff.md"],
    "deployment": ["deployment_log.md", "release_notes.md"],
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Stage:
    """Represents a single stage in the swarm execution plan."""
    stage_id: int
    name: str
    agents: list[str]
    skills: list[str]
    dependencies: list[int]
    parallelizable: bool
    outputs: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Plan:
    """Top-level swarm execution plan."""
    task_summary: str
    complexity: str
    stages: list[Stage]
    dependency_graph: dict[str, list[int]]
    critical_path: list[int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_summary": self.task_summary,
            "complexity": self.complexity,
            "stages": [s.to_dict() for s in self.stages],
            "dependency_graph": self.dependency_graph,
            "critical_path": self.critical_path,
        }


# ---------------------------------------------------------------------------
# Task parsing
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase and strip punctuation for keyword matching."""
    return re.sub(r"[^\w\s]", " ", text.lower())


def detect_stages(task_description: str) -> list[str]:
    """Detect which pipeline stages are implied by the task description."""
    normalized = _normalize(task_description)
    detected: list[str] = []
    scores: dict[str, int] = {}

    for stage, keywords in STAGE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in normalized)
        if score:
            scores[stage] = score

    # Sort by default pipeline order so dependencies make sense
    for stage in STAGE_ORDER_DEFAULT:
        if stage in scores:
            detected.append(stage)

    # If nothing matched, default to a generic implementation + documentation flow
    if not detected:
        detected = ["implementation", "documentation"]

    logger.info("Detected stages: %s", detected)
    return detected


def estimate_complexity(task_description: str, stage_count: int) -> str:
    """Estimate task complexity based on heuristics."""
    desc_lower = task_description.lower()
    word_count = len(desc_lower.split())

    # Signals of complexity
    complexity_score = 0

    complex_signals = [
        "architecture", "distributed", "microservice", "scalable",
        "enterprise", "multi-step", "end-to-end", "full stack",
        "comprehensive", "extensive", "deep dive", "thorough",
        "production-grade", "high-performance", "real-time",
    ]
    simple_signals = [
        "simple", "quick", "brief", "short", "basic", "minimal",
        "overview", "summary", "high-level", "snippet", "example",
    ]

    for sig in complex_signals:
        if sig in desc_lower:
            complexity_score += 2
    for sig in simple_signals:
        if sig in desc_lower:
            complexity_score -= 2

    # Stage count contributes
    if stage_count >= 6:
        complexity_score += 3
    elif stage_count >= 4:
        complexity_score += 1
    elif stage_count <= 2:
        complexity_score -= 1

    # Word count of description
    if word_count > 50:
        complexity_score += 1
    if word_count > 100:
        complexity_score += 1

    if complexity_score >= 4:
        return "complex"
    elif complexity_score >= 1:
        return "moderate"
    return "simple"


def recommend_agents(stage_name: str) -> tuple[list[str], list[str]]:
    """Recommend agent types and skills for a given stage."""
    agents: list[str] = []
    skills: set[str] = set()

    for agent_id, meta in AGENT_CATALOG.items():
        if stage_name in meta.get("stage_hint", []):
            agents.append(agent_id)
            skills.update(meta.get("skills", []))

    # Fallback: if no specific agents matched, assign a generalist
    if not agents:
        if stage_name in ("research",):
            agents = ["researcher-market"]
        elif stage_name in ("implementation",):
            agents = ["developer-fullstack"]
        elif stage_name in ("documentation",):
            agents = ["writer-technical"]
        else:
            agents = ["developer-fullstack"]

        for a in agents:
            skills.update(AGENT_CATALOG.get(a, {}).get("skills", []))

    return agents, sorted(skills)


# ---------------------------------------------------------------------------
# Dependency graph & critical path
# ---------------------------------------------------------------------------

def build_dependencies(
    stages: list[str], max_agents: int
) -> tuple[dict[str, list[int]], list[int]]:
    """
    Build dependency graph and identify critical path.

    Returns:
        - dependency_graph: stage_id (1-based) -> list of dependency stage_ids
        - critical_path: ordered list of stage_ids on the critical path
    """
    # Map stage name -> id (1-based)
    stage_ids = {name: idx + 1 for idx, name in enumerate(stages)}

    dep_graph: dict[str, list[int]] = {}

    # Default sequential dependencies with parallelization heuristics
    for idx, stage in enumerate(stages):
        sid = idx + 1
        if idx == 0:
            dep_graph[str(sid)] = []
        else:
            # Research + analysis can sometimes be parallelized
            if stage in ("analysis",) and "research" in stages and sid <= max_agents:
                dep_graph[str(sid)] = []
            # Design and implementation are usually sequential
            # Testing usually depends on implementation
            elif stage == "testing" and "implementation" in stage_ids:
                dep_graph[str(sid)] = [stage_ids["implementation"]]
            # Integration depends on implementation (and optionally testing)
            elif stage == "integration" and "implementation" in stage_ids:
                deps = [stage_ids["implementation"]]
                if "testing" in stage_ids:
                    deps.append(stage_ids["testing"])
                dep_graph[str(sid)] = sorted(set(deps))
            # Documentation can often be parallel with testing/review
            elif stage == "documentation" and "implementation" in stage_ids:
                dep_graph[str(sid)] = [stage_ids["implementation"]]
            # Review depends on most prior stages
            elif stage == "review":
                deps = [stage_ids[s] for s in stages[:idx] if s in stage_ids]
                # Cap dependencies to avoid explosion; depend on last substantive stage
                if "documentation" in stage_ids and stage_ids["documentation"] in deps:
                    dep_graph[str(sid)] = [stage_ids["documentation"]]
                elif "testing" in stage_ids and stage_ids["testing"] in deps:
                    dep_graph[str(sid)] = [stage_ids["testing"]]
                elif "implementation" in stage_ids and stage_ids["implementation"] in deps:
                    dep_graph[str(sid)] = [stage_ids["implementation"]]
                else:
                    dep_graph[str(sid)] = [sid - 1] if sid > 1 else []
            # Deployment depends on testing and review
            elif stage == "deployment":
                deps = []
                if "review" in stage_ids:
                    deps.append(stage_ids["review"])
                elif "testing" in stage_ids:
                    deps.append(stage_ids["testing"])
                elif "integration" in stage_ids:
                    deps.append(stage_ids["integration"])
                dep_graph[str(sid)] = sorted(set(deps)) if deps else ([sid - 1] if sid > 1 else [])
            else:
                dep_graph[str(sid)] = [sid - 1] if sid > 1 else []

    # Critical path = longest path from first to last stage (simplified: sequential)
    critical_path = list(range(1, len(stages) + 1))

    return dep_graph, critical_path


def compute_parallelization(
    stages: list[str], dep_graph: dict[str, list[int]]
) -> dict[str, bool]:
    """Determine which stages can run in parallel based on dependencies."""
    parallel: dict[str, bool] = {}
    for idx, stage in enumerate(stages):
        sid = str(idx + 1)
        deps = dep_graph.get(sid, [])
        # A stage is parallelizable if it has no deps or only soft deps
        # and the stage type itself is commonly parallel-friendly
        parallel[sid] = (
            len(deps) == 0
            or stage in ("documentation", "research")
        ) and stage not in ("deployment", "review", "integration")
    return parallel


# ---------------------------------------------------------------------------
# Plan generation
# ---------------------------------------------------------------------------

def generate_plan(task_description: str, max_agents: int) -> Plan:
    """Generate a full swarm execution plan from a task description."""
    if not task_description or not task_description.strip():
        raise ValueError("Task description cannot be empty.")

    task_summary = task_description.strip()
    detected_stages = detect_stages(task_description)
    complexity = estimate_complexity(task_description, len(detected_stages))

    dep_graph, critical_path = build_dependencies(detected_stages, max_agents)
    parallel_map = compute_parallelization(detected_stages, dep_graph)

    stages: list[Stage] = []
    for idx, stage_name in enumerate(detected_stages):
        sid = idx + 1
        agents, skills = recommend_agents(stage_name)
        outputs = STAGE_OUTPUTS.get(stage_name, [f"{stage_name}_output.md"])
        stages.append(
            Stage(
                stage_id=sid,
                name=stage_name.capitalize(),
                agents=agents,
                skills=skills,
                dependencies=dep_graph.get(str(sid), []),
                parallelizable=parallel_map.get(str(sid), False),
                outputs=outputs,
            )
        )

    plan = Plan(
        task_summary=task_summary,
        complexity=complexity,
        stages=stages,
        dependency_graph=dep_graph,
        critical_path=critical_path,
    )

    return plan


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def plan_to_markdown(plan: Plan) -> str:
    """Render a Plan as Markdown for human review."""
    lines: list[str] = []
    lines.append(f"# Swarm Execution Plan\n")
    lines.append(f"**Task Summary:** {plan.task_summary}\n")
    lines.append(f"**Complexity:** `{plan.complexity.upper()}`\n")
    lines.append(f"**Total Stages:** {len(plan.stages)}\n")
    lines.append("---\n")

    # Stages
    lines.append("## Stages\n")
    for stage in plan.stages:
        lines.append(f"### Stage {stage.stage_id}: {stage.name}\n")
        lines.append(f"- **Agents:** {', '.join(stage.agents)}")
        lines.append(f"- **Skills:** {', '.join(stage.skills)}")
        deps_str = ", ".join(str(d) for d in stage.dependencies) if stage.dependencies else "None"
        lines.append(f"- **Dependencies:** {deps_str}")
        lines.append(f"- **Parallelizable:** {'Yes' if stage.parallelizable else 'No'}")
        lines.append(f"- **Expected Outputs:** {', '.join(stage.outputs)}")
        lines.append("")

    # Dependency Graph
    lines.append("## Dependency Graph\n")
    lines.append("```json")
    lines.append(json.dumps(plan.dependency_graph, indent=2))
    lines.append("```\n")

    # Critical Path
    lines.append("## Critical Path\n")
    path_names = []
    for sid in plan.critical_path:
        for s in plan.stages:
            if s.stage_id == sid:
                path_names.append(f"{sid}. {s.name}")
                break
    lines.append(" → ".join(path_names))
    lines.append("\n")

    # Parallelization Opportunities
    lines.append("## Parallelization Opportunities\n")
    parallel_stages = [s for s in plan.stages if s.parallelizable]
    if parallel_stages:
        lines.append("The following stages may run in parallel:\n")
        for s in parallel_stages:
            lines.append(f"- **Stage {s.stage_id}:** {s.name}")
    else:
        lines.append("No parallelization opportunities detected. All stages are sequential.")
    lines.append("\n")

    # Agent Summary
    lines.append("## Agent Summary\n")
    all_agents: set[str] = set()
    for s in plan.stages:
        all_agents.update(s.agents)
    for agent_id in sorted(all_agents):
        meta = AGENT_CATALOG.get(agent_id, {})
        desc = meta.get("description", "")
        lines.append(f"- **{agent_id}** — {desc}")
    lines.append("\n")

    # Mermaid diagram
    lines.append("## Dependency Diagram (Mermaid)\n")
    lines.append("```mermaid")
    lines.append("graph TD")
    for stage in plan.stages:
        node_id = f"S{stage.stage_id}"
        lines.append(f"    {node_id}[{stage.name}]")
    for stage in plan.stages:
        node_id = f"S{stage.stage_id}"
        for dep in stage.dependencies:
            lines.append(f"    S{dep} --> {node_id}")
    lines.append("```\n")

    return "\n".join(lines)


def plan_to_json(plan: Plan) -> str:
    """Serialize a Plan to a JSON string."""
    return json.dumps(plan.to_dict(), indent=2)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_plan(plan: Plan) -> list[str]:
    """Validate plan structure and return list of issues (empty if valid)."""
    issues: list[str] = []

    if not plan.task_summary.strip():
        issues.append("Task summary is empty.")

    if not plan.stages:
        issues.append("Plan has no stages.")

    stage_ids = [s.stage_id for s in plan.stages]
    if len(stage_ids) != len(set(stage_ids)):
        issues.append("Duplicate stage IDs detected.")

    expected_ids = list(range(1, len(plan.stages) + 1))
    if sorted(stage_ids) != expected_ids:
        issues.append(f"Stage IDs are not contiguous 1..N: {sorted(stage_ids)}")

    for stage in plan.stages:
        if not stage.agents:
            issues.append(f"Stage {stage.stage_id} has no assigned agents.")
        for dep in stage.dependencies:
            if dep < 1 or dep > len(plan.stages):
                issues.append(
                    f"Stage {stage.stage_id} has out-of-range dependency: {dep}"
                )

    # Check for dependency cycles (simple DFS)
    graph = {s.stage_id: s.dependencies for s in plan.stages}

    def has_cycle(node: int, visited: set[int], rec_stack: set[int]) -> bool:
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.remove(node)
        return False

    visited: set[int] = set()
    rec_stack: set[int] = set()
    for sid in graph:
        if sid not in visited:
            if has_cycle(sid, visited, rec_stack):
                issues.append("Dependency graph contains a cycle.")
                break

    return issues


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate structured swarm execution plans from task descriptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python swarm_plan_generator.py "Research AI trends and write a report" \\
                  --format markdown --output plan.md
              python swarm_plan_generator.py --task-file task.txt --format json --max-agents 5
              echo "Build a REST API" | python swarm_plan_generator.py --format json
        """),
    )

    # Input
    parser.add_argument(
        "task",
        nargs="?",
        help="Task description (inline). If omitted, reads from stdin or --task-file.",
    )
    parser.add_argument(
        "--task-file",
        type=Path,
        metavar="FILE",
        help="Path to a file containing the task description.",
    )

    # Output
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )

    # Constraints
    parser.add_argument(
        "--max-agents",
        type=int,
        default=10,
        metavar="N",
        help="Maximum number of agents that can run in parallel (default: 10).",
    )

    # Validation
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip plan structure validation.",
    )

    # Logging
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress non-error output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug logging.",
    )

    return parser.parse_args(argv)


def read_task_input(args: argparse.Namespace) -> str:
    """Resolve task description from inline arg, file, or stdin."""
    if args.task:
        return args.task

    if args.task_file:
        if not args.task_file.exists():
            logger.error("Task file not found: %s", args.task_file)
            sys.exit(1)
        return args.task_file.read_text(encoding="utf-8")

    # Read from stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    logger.error("No task description provided. Use positional argument, --task-file, or pipe via stdin.")
    sys.exit(1)


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    task_description = read_task_input(args)

    if args.max_agents < 1:
        logger.error("--max-agents must be >= 1")
        return 1

    logger.info("Generating plan for task (%d chars)...", len(task_description))

    try:
        plan = generate_plan(task_description, max_agents=args.max_agents)
    except ValueError as exc:
        logger.error("Plan generation failed: %s", exc)
        return 1

    # Validate
    if not args.skip_validation:
        issues = validate_plan(plan)
        if issues:
            logger.error("Plan validation failed:")
            for issue in issues:
                logger.error("  - %s", issue)
            return 1
        logger.info("Plan validation passed.")

    # Render output
    if args.format == "markdown":
        output = plan_to_markdown(plan)
    else:
        output = plan_to_json(plan)

    # Write
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
        if not args.quiet:
            print(f"Plan written to {args.output}")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
