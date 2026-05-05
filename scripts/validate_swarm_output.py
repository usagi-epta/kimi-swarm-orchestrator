#!/usr/bin/env python3
"""
Validate Swarm Output

Validates swarm-generated output files against expectation criteria across four
validation dimensions: completeness, correctness, format_compliance, and
integration_readiness.

Supports custom criteria via JSON file, hard/soft gate configuration, retry
recommendation generation, and structured pass/fail reporting.

Usage:
    python validate_swarm_output.py output.md --criteria criteria.json --report report.md
    python validate_swarm_output.py report.md --completeness --format-compliance --hard-gate
    python validate_swarm_output.py code.py --criteria-file test_criteria.json --format json
    python validate_swarm_output.py output.md --completeness --format-compliance \\
        --integration-readiness --correctness --report report.json
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
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("validate_swarm_output")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CRITERIA: dict[str, Any] = {
    "completeness": {
        "required_sections": [],
        "required_length": {},
        "hard_gate": True,
    },
    "correctness": {
        "verify_facts": False,
        "no_contradictions": True,
        "hard_gate": True,
    },
    "format_compliance": {
        "required_structure": "",
        "file_format": "",
        "hard_gate": False,
    },
    "integration_readiness": {
        "cross_reference_check": False,
        "naming_convention": "",
        "hard_gate": False,
    },
}

# Patterns commonly indicating contradictions
CONTRADICTION_PATTERNS: list[str] = [
    r"\bhowever\b.*?\b(however|but|although)\b",
    r"\b(false|incorrect|wrong)\b.*?\b(true|correct|right)\b",
    r"\b(always)\b.*?\b(never)\b",
    r"\b(increases?)\b.*?\b(decreases?)\b",
    r"\b(positive)\b.*?\b(negative)\b",
]

SUPPORTED_FILE_EXTENSIONS: set[str] = {
    ".md", ".txt", ".json", ".py", ".js", ".ts", ".yaml", ".yml",
    ".html", ".css", ".xml", ".csv", ".rst", ".java", ".go",
    ".rs", ".c", ".cpp", ".h", ".sh", ".rb", ".php", ".sql",
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class GateResult:
    """Result for a single validation dimension (gate)."""
    dimension: str
    ruling: str  # "PASS" | "FAIL" | "WARN"
    evidence: list[str] = field(default_factory=list)
    hard_gate: bool = False
    fix_suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    """Top-level validation report."""
    file: str
    overall: str  # "PASS" | "FAIL"
    gates: list[GateResult]
    retry_recommended: bool
    fix_suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "overall": self.overall,
            "gates": [g.to_dict() for g in self.gates],
            "retry_recommended": self.retry_recommended,
            "fix_suggestions": self.fix_suggestions,
        }


# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------

def read_file(file_path: Path) -> tuple[str, str]:
    """
    Read and return the contents of a file.

    Returns:
        Tuple of (raw_text, detected_format)

    Raises:
        SystemExit: if file cannot be read.
    """
    if not file_path.exists():
        logger.error("File not found: %s", file_path)
        sys.exit(1)

    if not file_path.is_file():
        logger.error("Path is not a file: %s", file_path)
        sys.exit(1)

    suffix = file_path.suffix.lower()
    if suffix not in SUPPORTED_FILE_EXTENSIONS:
        logger.warning(
            "File extension '%s' is not in the explicitly supported list. "
            "Attempting to read as text anyway.",
            suffix,
        )

    try:
        raw = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.error("File is not valid UTF-8 text: %s", file_path)
        sys.exit(1)
    except OSError as exc:
        logger.error("Cannot read file %s: %s", file_path, exc)
        sys.exit(1)

    if not raw.strip():
        logger.warning("File is empty: %s", file_path)

    detected_format = _detect_format(suffix, raw)
    return raw, detected_format


def _detect_format(suffix: str, raw: str) -> str:
    """Detect the format of the file contents."""
    if suffix == ".md":
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix in (".yaml", ".yml"):
        return "yaml"
    if suffix == ".py":
        return "python"
    if suffix in (".js", ".ts"):
        return "javascript"
    if suffix == ".html":
        return "html"
    if suffix == ".xml":
        return "xml"
    if suffix == ".csv":
        return "csv"
    if suffix == ".rst":
        return "rst"
    # Heuristic: check for markdown indicators
    if re.search(r"^#{1,6}\s", raw, re.MULTILINE):
        return "markdown"
    # Heuristic: check for JSON
    if raw.strip().startswith(("{", "[")):
        try:
            json.loads(raw)
            return "json"
        except json.JSONDecodeError:
            pass
    return "text"


# ---------------------------------------------------------------------------
# Criteria loading
# ---------------------------------------------------------------------------

def load_criteria(
    criteria_file: Path | None,
    cli_dimensions: set[str],
    hard_gate: bool,
) -> dict[str, Any]:
    """
    Load and merge criteria from file and CLI arguments.

    Args:
        criteria_file: Path to a JSON criteria file (optional).
        cli_dimensions: Set of dimension names enabled via CLI flags.
        hard_gate: If True, override all gates to be hard gates.

    Returns:
        Merged criteria dictionary.
    """
    criteria: dict[str, Any] = {}

    # Start from file if provided
    if criteria_file:
        if not criteria_file.exists():
            logger.error("Criteria file not found: %s", criteria_file)
            sys.exit(1)
        try:
            file_data = json.loads(criteria_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON in criteria file: %s", exc)
            sys.exit(1)
        if not isinstance(file_data, dict):
            logger.error("Criteria file must contain a JSON object.")
            sys.exit(1)
        criteria = file_data

    # Fill in missing dimensions from defaults
    for dim, default in DEFAULT_CRITERIA.items():
        if dim not in criteria:
            criteria[dim] = dict(default)

    # If CLI dimensions are specified, zero out criteria for unselected ones
    # but keep their structure so they still run (just with no requirements)
    if cli_dimensions:
        all_dims = set(DEFAULT_CRITERIA.keys())
        for dim in all_dims - cli_dimensions:
            # Keep dimension but clear requirements
            criteria[dim] = _empty_criteria_for_dimension(dim)

    # Apply global hard-gate override
    if hard_gate:
        for dim in criteria:
            if isinstance(criteria[dim], dict):
                criteria[dim]["hard_gate"] = True

    return criteria


def _empty_criteria_for_dimension(dim: str) -> dict[str, Any]:
    """Return a criteria dict for a dimension with no requirements."""
    base = dict(DEFAULT_CRITERIA.get(dim, {"hard_gate": False}))
    # Clear list/dict values
    for key, val in base.items():
        if isinstance(val, list):
            base[key] = []
        elif isinstance(val, dict):
            base[key] = {}
        elif isinstance(val, bool) and key != "hard_gate":
            base[key] = False
    return base


# ---------------------------------------------------------------------------
# Evaluators (one per dimension)
# ---------------------------------------------------------------------------

def evaluate_completeness(content: str, criteria: dict[str, Any]) -> GateResult:
    """
    Evaluate completeness dimension.

    Checks:
    - Required sections/headings are present
    - Minimum word count is met
    - Minimum line count is met
    - Non-empty content
    """
    dimension = "completeness"
    evidence: list[str] = []
    fix_suggestions: list[str] = []
    passed = True

    required_sections = criteria.get("required_sections", [])
    required_length = criteria.get("required_length", {})
    hard_gate = criteria.get("hard_gate", True)

    # Check non-empty
    stripped = content.strip()
    if not stripped:
        evidence.append("Content is empty.")
        fix_suggestions.append("Add substantive content to the output file.")
        passed = False
    else:
        evidence.append(f"Content present ({len(stripped)} characters).")

    # Check required sections (headings for Markdown, section markers for text)
    if required_sections:
        missing_sections: list[str] = []
        for section in required_sections:
            # Try multiple patterns: markdown heading, bold marker, plain text
            patterns = [
                rf"^#+\s*{re.escape(section)}",
                rf"^\*\*{re.escape(section)}\*\*",
                rf"^{re.escape(section)}",
            ]
            found = any(
                re.search(p, stripped, re.MULTILINE | re.IGNORECASE)
                for p in patterns
            )
            if found:
                evidence.append(f"Required section '{section}' found.")
            else:
                missing_sections.append(section)

        if missing_sections:
            for sec in missing_sections:
                evidence.append(f"Required section '{sec}' NOT found.")
                fix_suggestions.append(f"Add a section titled '{sec}'.")
            passed = False
        else:
            evidence.append(f"All {len(required_sections)} required sections present.")

    # Check length requirements
    words = stripped.split()
    word_count = len(words)
    lines = [ln for ln in stripped.splitlines() if ln.strip()]
    line_count = len(lines)

    if "min_words" in required_length:
        min_w = required_length["min_words"]
        if word_count >= min_w:
            evidence.append(f"{word_count} words (exceeds minimum of {min_w}).")
        else:
            evidence.append(f"{word_count} words (below minimum of {min_w}).")
            fix_suggestions.append(f"Expand content to at least {min_w} words.")
            passed = False

    if "max_words" in required_length:
        max_w = required_length["max_words"]
        if word_count <= max_w:
            evidence.append(f"{word_count} words (within maximum of {max_w}).")
        else:
            evidence.append(f"{word_count} words (exceeds maximum of {max_w}).")
            fix_suggestions.append(f"Reduce content to at most {max_w} words.")
            passed = False

    if "min_lines" in required_length:
        min_l = required_length["min_lines"]
        if line_count >= min_l:
            evidence.append(f"{line_count} non-empty lines (exceeds minimum of {min_l}).")
        else:
            evidence.append(f"{line_count} non-empty lines (below minimum of {min_l}).")
            fix_suggestions.append(f"Add more content to reach at least {min_l} lines.")
            passed = False

    return GateResult(
        dimension=dimension,
        ruling="PASS" if passed else "FAIL",
        evidence=evidence,
        hard_gate=hard_gate,
        fix_suggestions=fix_suggestions,
    )


def evaluate_correctness(content: str, criteria: dict[str, Any]) -> GateResult:
    """
    Evaluate correctness dimension.

    Checks:
    - No internal contradictions (heuristic)
    - No placeholder text (TODO, FIXME, XXX, TBD)
    - Basic fact-check heuristics (dates, numbers)
    """
    dimension = "correctness"
    evidence: list[str] = []
    fix_suggestions: list[str] = []
    passed = True

    verify_facts = criteria.get("verify_facts", False)
    no_contradictions = criteria.get("no_contradictions", True)
    hard_gate = criteria.get("hard_gate", True)

    # Check for placeholder text
    placeholders = re.findall(r"\b(TODO|FIXME|XXX|TBD|HACK|PLACEHOLDER|INSERT)\b", content, re.IGNORECASE)
    if placeholders:
        unique = sorted(set(p.upper() for p in placeholders))
        evidence.append(f"Placeholder markers found: {', '.join(unique)}.")
        fix_suggestions.append(f"Resolve placeholders: {', '.join(unique)}.")
        passed = False
    else:
        evidence.append("No placeholder markers (TODO/FIXME/etc.) detected.")

    # Contradiction detection (heuristic)
    if no_contradictions:
        contradictions_found = 0
        for pattern in CONTRADICTION_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            contradictions_found += len(matches)

        if contradictions_found > 0:
            evidence.append(
                f"{contradictions_found} potential contradiction(s) detected (heuristic)."
            )
            fix_suggestions.append("Review content for contradictory statements.")
            passed = False
        else:
            evidence.append("No obvious contradictions detected.")

    # Basic fact-check heuristics
    if verify_facts:
        # Check for suspicious date patterns (e.g., year 9999, invalid dates)
        suspicious_years = re.findall(r"\b(9999|0000|1234)\b", content)
        if suspicious_years:
            evidence.append(f"Suspicious year values detected: {suspicious_years}.")
            fix_suggestions.append("Verify date/year values are correct.")
            passed = False

        # Check for unmatched parentheses or brackets (common error)
        open_parens = content.count("(")
        close_parens = content.count(")")
        if open_parens != close_parens:
            evidence.append(
                f"Unmatched parentheses: {open_parens} open, {close_parens} close."
            )
            fix_suggestions.append("Fix unmatched parentheses.")
            passed = False
        else:
            evidence.append("Parentheses are balanced.")
    else:
        evidence.append("Fact verification skipped (not enabled in criteria).")

    return GateResult(
        dimension=dimension,
        ruling="PASS" if passed else "FAIL",
        evidence=evidence,
        hard_gate=hard_gate,
        fix_suggestions=fix_suggestions,
    )


def evaluate_format_compliance(
    content: str, criteria: dict[str, Any], detected_format: str
) -> GateResult:
    """
    Evaluate format compliance dimension.

    Checks:
    - File format matches expected format
    - Required structure type is satisfied
    - Valid JSON/YAML if applicable
    - Proper Markdown structure if applicable
    """
    dimension = "format_compliance"
    evidence: list[str] = []
    fix_suggestions: list[str] = []
    passed = True

    required_structure = criteria.get("required_structure", "")
    file_format = criteria.get("file_format", "")
    hard_gate = criteria.get("hard_gate", False)

    # Check file format
    if file_format:
        if detected_format.lower() == file_format.lower():
            evidence.append(f"Detected format '{detected_format}' matches expected '{file_format}'.")
        else:
            evidence.append(
                f"Detected format '{detected_format}' does NOT match expected '{file_format}'."
            )
            fix_suggestions.append(f"Convert file to {file_format} format.")
            passed = False
    else:
        evidence.append(f"No format requirement specified; detected '{detected_format}'.")

    # Check required structure
    if required_structure:
        struct_lower = required_structure.lower()
        if struct_lower == "report":
            # Reports should have headings
            has_headings = bool(re.search(r"^#{1,6}\s", content, re.MULTILINE))
            has_paragraphs = len([p for p in content.split("\n\n") if p.strip()]) >= 2
            if has_headings and has_paragraphs:
                evidence.append("Report structure detected (headings + paragraphs).")
            else:
                if not has_headings:
                    evidence.append("Report structure missing: no headings found.")
                    fix_suggestions.append("Add markdown headings (## Section) to structure the report.")
                if not has_paragraphs:
                    evidence.append("Report structure missing: insufficient paragraphs.")
                    fix_suggestions.append("Add more descriptive paragraphs.")
                passed = False
        elif struct_lower == "code":
            # Code files should have function/class definitions or executable statements
            has_code = bool(
                re.search(r"^(def |class |import |const |function |var |let )", content, re.MULTILINE)
                or re.search(r"[;{}=]", content)
            )
            if has_code:
                evidence.append("Code structure detected.")
            else:
                evidence.append("Code structure NOT detected.")
                fix_suggestions.append("Ensure file contains valid code constructs.")
                passed = False
        elif struct_lower == "json":
            try:
                json.loads(content)
                evidence.append("Valid JSON structure.")
            except json.JSONDecodeError as exc:
                evidence.append(f"Invalid JSON: {exc}")
                fix_suggestions.append("Fix JSON syntax errors.")
                passed = False
        else:
            evidence.append(f"Structure check '{required_structure}' not implemented; skipping.")

    # Format-specific validation
    if detected_format == "markdown":
        # Check for common markdown issues
        if content.strip() and not re.search(r"^#{1,6}\s", content, re.MULTILINE):
            evidence.append("Warning: Markdown file has no headings.")
            fix_suggestions.append("Add markdown headings for better structure.")
            # This is just a warning, not a failure
        else:
            heading_count = len(re.findall(r"^#{1,6}\s", content, re.MULTILINE))
            evidence.append(f"Markdown headings found: {heading_count}.")

    elif detected_format == "json":
        try:
            parsed = json.loads(content)
            evidence.append("Valid JSON syntax.")
            if isinstance(parsed, dict):
                evidence.append(f"JSON object with {len(parsed)} top-level keys.")
        except json.JSONDecodeError as exc:
            evidence.append(f"Invalid JSON syntax: {exc}")
            fix_suggestions.append("Fix JSON syntax errors.")
            passed = False

    elif detected_format == "python":
        # Basic Python syntax check
        try:
            compile(content, "<string>", "exec")
            evidence.append("Python syntax compiles successfully.")
        except SyntaxError as exc:
            evidence.append(f"Python syntax error: {exc}")
            fix_suggestions.append("Fix Python syntax errors.")
            passed = False

    return GateResult(
        dimension=dimension,
        ruling="PASS" if passed else "FAIL",
        evidence=evidence,
        hard_gate=hard_gate,
        fix_suggestions=fix_suggestions,
    )


def evaluate_integration_readiness(
    content: str, criteria: dict[str, Any]
) -> GateResult:
    """
    Evaluate integration readiness dimension.

    Checks:
    - Cross-references are consistent (heuristic)
    - Naming conventions are followed
    - No broken internal references
    - Dependencies are declared
    """
    dimension = "integration_readiness"
    evidence: list[str] = []
    fix_suggestions: list[str] = []
    passed = True

    cross_reference_check = criteria.get("cross_reference_check", False)
    naming_convention = criteria.get("naming_convention", "")
    hard_gate = criteria.get("hard_gate", False)

    # Cross-reference check (heuristic for markdown links, file refs)
    if cross_reference_check:
        # Find markdown-style links
        md_links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)
        broken_refs: list[str] = []
        for label, target in md_links:
            # If target looks like a relative file path, note it
            if target.startswith(("./", "../")) and not target.startswith(("http://", "https://")):
                # We can't verify filesystem from content alone, just flag it
                pass

        # Find reference-style links that might be broken
        ref_defs = set(re.findall(r"^\[([^\]]+)\]:\s", content, re.MULTILINE))
        ref_uses = set(re.findall(r"\[([^\]]+)\](?:\[[^\]]*\])?", content))
        # Simple heuristic
        if md_links:
            evidence.append(f"Found {len(md_links)} markdown link(s).")
        else:
            evidence.append("No markdown cross-references found.")

        # Check for file references that look like placeholders
        file_refs = re.findall(r"`?([\w\-./]+\.(md|py|json|yaml|yml|js|ts|sh))`?", content)
        if file_refs:
            evidence.append(f"Found {len(file_refs)} file reference(s).")
    else:
        evidence.append("Cross-reference check skipped (not enabled).")

    # Naming convention check
    if naming_convention:
        nc = naming_convention.lower()
        if nc == "kebab-case":
            # Check for snake_case or camelCase violations in file references
            snake_refs = re.findall(r"`?([a-z]+_[a-z_]+\.(py|md|js|ts|json|yaml))`?", content)
            camel_refs = re.findall(r"`?([a-z]+[A-Z][a-zA-Z]*\.(py|md|js|ts|json|yaml))`?", content)
            if snake_refs:
                evidence.append(f"Found {len(snake_refs)} snake_case file reference(s).")
                fix_suggestions.append("Use kebab-case for file names (e.g., 'my-file.py' not 'my_file.py').")
                passed = False
            elif camel_refs:
                evidence.append(f"Found {len(camel_refs)} camelCase file reference(s).")
                fix_suggestions.append("Use kebab-case for file names (e.g., 'my-file.py' not 'myFile.py').")
                passed = False
            else:
                evidence.append("Naming appears to follow kebab-case convention.")
        elif nc == "snake_case":
            # Reverse check
            kebab_refs = re.findall(r"`?([a-z]+-[a-z\-]+\.(py|md|js|ts|json|yaml))`?", content)
            if kebab_refs:
                evidence.append(f"Found {len(kebab_refs)} kebab-case file reference(s).")
                fix_suggestions.append("Use snake_case for file names (e.g., 'my_file.py' not 'my-file.py').")
                passed = False
            else:
                evidence.append("Naming appears to follow snake_case convention.")
        elif nc == "camelcase":
            evidence.append("camelCase naming convention check not fully implemented.")
        else:
            evidence.append(f"Unknown naming convention '{naming_convention}'; skipping.")
    else:
        evidence.append("No naming convention requirement specified.")

    # General integration signals
    if "import " in content or "from " in content or "require(" in content or "dependencies" in content.lower():
        evidence.append("Dependency declarations detected.")
    if "TODO" in content or "FIXME" in content:
        evidence.append("Warning: TODO/FIXME markers may block integration.")
        fix_suggestions.append("Resolve all TODO/FIXME markers before integration.")
        # This is a warning, not necessarily a failure for soft gates

    return GateResult(
        dimension=dimension,
        ruling="PASS" if passed else "FAIL",
        evidence=evidence,
        hard_gate=hard_gate,
        fix_suggestions=fix_suggestions,
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    file_path: Path,
    content: str,
    criteria: dict[str, Any],
    detected_format: str,
) -> ValidationReport:
    """
    Run all enabled validation dimensions and produce a report.

    Args:
        file_path: Path to the validated file.
        content: File contents.
        criteria: Merged criteria dictionary.
        detected_format: Detected file format string.

    Returns:
        ValidationReport with overall PASS/FAIL and per-gate results.
    """
    gates: list[GateResult] = []

    # Always evaluate all four dimensions (criteria may be empty for unselected ones)
    evaluators = {
        "completeness": evaluate_completeness,
        "correctness": evaluate_correctness,
        "format_compliance": lambda c, cr: evaluate_format_compliance(c, cr, detected_format),
        "integration_readiness": evaluate_integration_readiness,
    }

    retry_recommended = False
    all_fixes: list[str] = []

    for dim_name, evaluator in evaluators.items():
        dim_criteria = criteria.get(dim_name, {})
        result = evaluator(content, dim_criteria)
        gates.append(result)

        if result.ruling == "FAIL":
            if result.hard_gate:
                retry_recommended = True
            all_fixes.extend(result.fix_suggestions)

    # Determine overall: FAIL if any hard_gate dimension fails
    overall = "PASS"
    for g in gates:
        if g.ruling == "FAIL" and g.hard_gate:
            overall = "FAIL"
            break

    # De-duplicate fix suggestions
    seen: set[str] = set()
    unique_fixes: list[str] = []
    for f in all_fixes:
        if f not in seen:
            seen.add(f)
            unique_fixes.append(f)

    return ValidationReport(
        file=str(file_path),
        overall=overall,
        gates=gates,
        retry_recommended=retry_recommended,
        fix_suggestions=unique_fixes,
    )


def report_to_json(report: ValidationReport) -> str:
    """Serialize report to JSON."""
    return json.dumps(report.to_dict(), indent=2)


def report_to_markdown(report: ValidationReport) -> str:
    """Render report as Markdown."""
    lines: list[str] = []

    overall_icon = "✓" if report.overall == "PASS" else "✗"
    lines.append(f"# Swarm Output Validation Report\n")
    lines.append(f"**File:** `{report.file}`\n")
    lines.append(f"**Overall:** {overall_icon} **{report.overall}**\n")
    lines.append(f"**Retry Recommended:** {'Yes' if report.retry_recommended else 'No'}\n")
    lines.append("---\n")

    for gate in report.gates:
        icon = "✓" if gate.ruling == "PASS" else "✗" if gate.ruling == "FAIL" else "⚠"
        gate_type = "HARD" if gate.hard_gate else "SOFT"
        lines.append(f"## {icon} {gate.dimension.title()} ({gate_type} GATE) — {gate.ruling}\n")

        lines.append("**Evidence:**")
        for ev in gate.evidence:
            lines.append(f"- {ev}")
        lines.append("")

        if gate.fix_suggestions:
            lines.append("**Fix Suggestions:**")
            for fix in gate.fix_suggestions:
                lines.append(f"- {fix}")
            lines.append("")

    if report.fix_suggestions:
        lines.append("## Consolidated Fix List\n")
        for i, fix in enumerate(report.fix_suggestions, 1):
            lines.append(f"{i}. {fix}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate swarm output files against expectation criteria.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python validate_swarm_output.py output.md --criteria criteria.json --report report.md
              python validate_swarm_output.py report.md --completeness --format-compliance --hard-gate
              python validate_swarm_output.py code.py --criteria-file test_criteria.json --format json
        """),
    )

    # Input
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the output file to validate.",
    )

    # Criteria source (file overrides CLI)
    parser.add_argument(
        "--criteria",
        "--criteria-file",
        dest="criteria_file",
        type=Path,
        metavar="FILE",
        help="JSON file with validation criteria.",
    )

    # Dimension toggles (used when no criteria file provided)
    parser.add_argument(
        "--completeness",
        action="store_true",
        help="Enable completeness validation.",
    )
    parser.add_argument(
        "--correctness",
        action="store_true",
        help="Enable correctness validation.",
    )
    parser.add_argument(
        "--format-compliance",
        action="store_true",
        dest="format_compliance",
        help="Enable format compliance validation.",
    )
    parser.add_argument(
        "--integration-readiness",
        action="store_true",
        dest="integration_readiness",
        help="Enable integration readiness validation.",
    )

    # Global hard-gate override
    parser.add_argument(
        "--hard-gate",
        action="store_true",
        dest="hard_gate",
        help="Treat all gates as hard gates (block on failure).",
    )

    # Output
    parser.add_argument(
        "--report",
        type=Path,
        metavar="FILE",
        help="Write validation report to FILE (format inferred from extension: .json or .md).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default=None,
        help="Report output format (default: inferred from --report extension, else json).",
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
        help="Enable verbose logging.",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine which dimensions to evaluate
    cli_dimensions: set[str] = set()
    if args.completeness:
        cli_dimensions.add("completeness")
    if args.correctness:
        cli_dimensions.add("correctness")
    if args.format_compliance:
        cli_dimensions.add("format_compliance")
    if args.integration_readiness:
        cli_dimensions.add("integration_readiness")

    # If no dimensions specified and no criteria file, default to all
    if not cli_dimensions and not args.criteria_file:
        cli_dimensions = set(DEFAULT_CRITERIA.keys())

    # Load criteria
    criteria = load_criteria(args.criteria_file, cli_dimensions, args.hard_gate)

    # Read the output file
    content, detected_format = read_file(args.file)
    logger.info("Validating '%s' (detected format: %s)", args.file, detected_format)

    # Run validation
    report = generate_report(args.file, content, criteria, detected_format)

    # Determine report format
    report_format = args.format
    if report_format is None and args.report:
        if args.report.suffix.lower() == ".md":
            report_format = "markdown"
        else:
            report_format = "json"
    if report_format is None:
        report_format = "json"

    # Render report
    if report_format == "markdown":
        report_text = report_to_markdown(report)
    else:
        report_text = report_to_json(report)

    # Write or print
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report_text, encoding="utf-8")
        if not args.quiet:
            print(f"Report written to {args.report}")
    else:
        print(report_text)

    # Exit code
    return 0 if report.overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
