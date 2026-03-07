#!/usr/bin/env python3
"""
HVS Skill Library Auditor
Checks all skills (or a single skill) against the HVS system standard.

Usage:
    # Audit all user skills
    python3 audit-skills.py --skills-dir /mnt/skills/user

    # Audit a single skill (e.g., a new skill being developed)
    python3 audit-skills.py --single /tmp/my-new-skill

    # Full audit with standard reference
    python3 audit-skills.py \
        --skills-dir /mnt/skills/user \
        --standard /mnt/skills/user/hvs-skill-buddy/references/hvs-system-standard.md
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    severity: str  # CRITICAL | WARNING | INFO | PASS
    skill: str
    check: str
    detail: str
    fix: str = ""


@dataclass
class AuditResult:
    skill: str
    findings: list = field(default_factory=list)

    @property
    def critical(self):
        return [f for f in self.findings if f.severity == "CRITICAL"]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == "WARNING"]

    @property
    def info(self):
        return [f for f in self.findings if f.severity == "INFO"]

    @property
    def passed(self):
        return [f for f in self.findings if f.severity == "PASS"]


# ──────────────────────────────────────────────────────────────────────────────
# Checks
# ──────────────────────────────────────────────────────────────────────────────

CANONICAL_PLAYWRIGHT_PIP = "pip install playwright pytest-playwright --break-system-packages"
CANONICAL_PLAYWRIGHT_BROWSERS = "playwright install --with-deps chromium"

def check_frontmatter(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    # Must have YAML frontmatter
    if not content.startswith("---"):
        findings.append(Finding(
            severity="CRITICAL",
            skill=name,
            check="frontmatter",
            detail="No YAML frontmatter found",
            fix="Add --- frontmatter block with name and description fields"
        ))
        return findings

    # Extract frontmatter
    end = content.find("---", 3)
    if end == -1:
        findings.append(Finding(
            severity="CRITICAL",
            skill=name,
            check="frontmatter",
            detail="Frontmatter block not closed",
            fix="Ensure frontmatter has opening and closing ---"
        ))
        return findings

    fm = content[3:end]

    # name field
    if "name:" not in fm:
        findings.append(Finding(
            severity="CRITICAL",
            skill=name,
            check="frontmatter.name",
            detail="Missing 'name' field in frontmatter",
            fix=f"Add 'name: {name}' to frontmatter"
        ))
    else:
        fm_name = re.search(r"name:\s*([^\n]+)", fm)
        if fm_name:
            extracted = fm_name.group(1).strip().strip("'\"")
            if extracted != name:
                findings.append(Finding(
                    severity="WARNING",
                    skill=name,
                    check="frontmatter.name",
                    detail=f"Skill name '{extracted}' doesn't match directory name '{name}'",
                    fix=f"Change name field to: name: {name}"
                ))

    # description field
    if "description:" not in fm:
        findings.append(Finding(
            severity="CRITICAL",
            skill=name,
            check="frontmatter.description",
            detail="Missing 'description' field in frontmatter",
            fix="Add a description field with trigger keywords"
        ))
    else:
        # Check for trigger keywords
        desc_match = re.search(r"description:(.+?)(?=\n\w|\Z)", fm, re.DOTALL)
        if desc_match:
            desc_text = desc_match.group(1)
            if "ALWAYS" not in desc_text and "Use when" not in desc_text and "trigger" not in desc_text.lower():
                findings.append(Finding(
                    severity="WARNING",
                    skill=name,
                    check="frontmatter.description",
                    detail="Description lacks trigger keywords (ALWAYS / Use when / trigger on)",
                    fix="Add explicit trigger phrases to description"
                ))

    return findings


def check_pip_installs(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    pip_lines = [l.strip() for l in content.split("\n")
                 if "pip install" in l
                 and not l.strip().startswith("#")
                 and not l.strip().startswith("RUN pip")]  # Dockerfile syntax exempted

    for line in pip_lines:
        if "--break-system-packages" not in line:
            findings.append(Finding(
                severity="CRITICAL",
                skill=name,
                check="pip.break-system-packages",
                detail=f"pip install missing --break-system-packages: {line[:80]}",
                fix=f"Add --break-system-packages to: {line[:60]}..."
            ))

    return findings


def check_playwright(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    has_playwright_ref = "playwright" in content.lower()
    if not has_playwright_ref:
        return findings  # Playwright not mentioned, skip

    pip_lines = [l.strip() for l in content.split("\n")
                 if "pip install" in l and "playwright" in l.lower()
                 and not l.strip().startswith("#")]

    for line in pip_lines:
        # Check canonical form
        has_playwright_pkg = re.search(r"pip install.*\bplaywright\b", line)
        has_pytest_playwright = "pytest-playwright" in line
        has_break = "--break-system-packages" in line

        issues = []
        if not has_playwright_pkg:
            issues.append("missing 'playwright' package")
        if not has_pytest_playwright:
            issues.append("missing 'pytest-playwright' package")
        if not has_break:
            issues.append("missing --break-system-packages")

        if issues:
            findings.append(Finding(
                severity="CRITICAL",
                skill=name,
                check="playwright.install",
                detail=f"Non-canonical Playwright install ({', '.join(issues)}): {line[:80]}",
                fix=f"Use canonical form: {CANONICAL_PLAYWRIGHT_PIP}"
            ))

    return findings


def check_npm_optional(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    npm_lines = [l.strip() for l in content.split("\n")
                 if "npm install" in l and not l.strip().startswith("#")]

    # Optional tool patterns (these should have 2>/dev/null || true)
    optional_patterns = ["@playwright/cli", "playwright-cli"]

    for line in npm_lines:
        for opt in optional_patterns:
            if opt in line and "2>/dev/null" not in line:
                findings.append(Finding(
                    severity="WARNING",
                    skill=name,
                    check="npm.optional-suppress",
                    detail=f"Optional npm tool '{opt}' should use '2>/dev/null || true': {line[:80]}",
                    fix=f"Append '2>/dev/null || true' to: {line[:60]}"
                ))

    return findings


def check_structure(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name
    line_count = content.count("\n")

    # Check references dir for long skills
    if line_count > 200:
        refs_dir = skill_path / "references"
        if not refs_dir.exists():
            findings.append(Finding(
                severity="WARNING",
                skill=name,
                check="structure.references",
                detail=f"Skill is {line_count} lines but has no references/ directory",
                fix="Create references/ and move detailed content into separate .md files"
            ))

    # Check for dangling references (files mentioned but not present)
    ref_mentions = re.findall(r"`references/([^`]+)`", content)
    refs_dir = skill_path / "references"
    for ref in ref_mentions:
        # Skip template placeholders like {adk-name}.md or <db>.md
        if re.search(r"[{<]", ref):
            continue
        ref_path = refs_dir / ref
        if not ref_path.exists():
            findings.append(Finding(
                severity="CRITICAL",
                skill=name,
                check="structure.dangling-ref",
                detail=f"SKILL.md references 'references/{ref}' but file does not exist",
                fix=f"Create references/{ref} or remove the reference from SKILL.md"
            ))

    # Check for dangling script references
    script_mentions = re.findall(r"`scripts/([^`]+)`", content)
    scripts_dir = skill_path / "scripts"
    for script in script_mentions:
        script_path = scripts_dir / script
        if not script_path.exists():
            findings.append(Finding(
                severity="CRITICAL",
                skill=name,
                check="structure.dangling-script",
                detail=f"SKILL.md references 'scripts/{script}' but file does not exist",
                fix=f"Create scripts/{script} or remove the reference from SKILL.md"
            ))

    # Check line count ceiling
    if line_count > 500:
        findings.append(Finding(
            severity="WARNING",
            skill=name,
            check="structure.length",
            detail=f"SKILL.md is {line_count} lines (limit is 500)",
            fix="Move detailed content to references/ files and add pointers"
        ))

    return findings


def check_phase_numbering(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    phases = re.findall(r"^## Phase (\d+)", content, re.MULTILINE)
    if not phases:
        return findings  # No phases used, fine for simpler skills

    nums = [int(p) for p in phases]
    if nums[0] == 0:
        findings.append(Finding(
            severity="WARNING",
            skill=name,
            check="phases.zero-indexed",
            detail="Phases start at 0; HVS standard requires starting at 1",
            fix="Renumber phases starting from Phase 1"
        ))

    # Check for gaps
    expected = list(range(nums[0], nums[0] + len(nums)))
    if nums != expected:
        findings.append(Finding(
            severity="INFO",
            skill=name,
            check="phases.numbering",
            detail=f"Phase numbers are not sequential: {nums}",
            fix="Renumber phases sequentially"
        ))

    return findings


def check_output_dir(skill_path: Path, content: str) -> list[Finding]:
    findings = []
    name = skill_path.name

    # Look for output patterns that don't use /tmp/hvs- prefix
    output_patterns = re.findall(r'mkdir\s+-p\s+"?([^"\s]+)"?', content)
    for pattern in output_patterns:
        if pattern.startswith("/tmp/") and not pattern.startswith("/tmp/hvs-"):
            findings.append(Finding(
                severity="INFO",
                skill=name,
                check="output.naming",
                detail=f"Output dir '{pattern}' should use /tmp/hvs-[skill]-[timestamp] prefix",
                fix=f'Use: OUTDIR="/tmp/hvs-{name}-$(date +%Y%m%d-%H%M%S)"'
            ))

    return findings


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

CHECKS = [
    check_frontmatter,
    check_pip_installs,
    check_playwright,
    check_npm_optional,
    check_structure,
    check_phase_numbering,
    check_output_dir,
]


def audit_skill(skill_dir: Path) -> AuditResult:
    """Audit a single skill directory."""
    result = AuditResult(skill=skill_dir.name)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        result.findings.append(Finding(
            severity="CRITICAL",
            skill=skill_dir.name,
            check="existence",
            detail="SKILL.md not found",
            fix="Create a SKILL.md file in the skill directory"
        ))
        return result

    content = skill_md.read_text()

    for check_fn in CHECKS:
        try:
            findings = check_fn(skill_dir, content)
            result.findings.extend(findings)
        except Exception as e:
            result.findings.append(Finding(
                severity="INFO",
                skill=skill_dir.name,
                check=check_fn.__name__,
                detail=f"Check failed with error: {e}",
                fix="Investigate check_fn manually"
            ))

    if not result.findings:
        result.findings.append(Finding(
            severity="PASS",
            skill=skill_dir.name,
            check="all",
            detail="No issues found",
        ))

    return result


def format_report(results: list[AuditResult], timestamp: str) -> str:
    lines = [
        "# HVS Skill Library Audit Report",
        f"Generated: {timestamp}",
        f"Skills audited: {len(results)}",
        "",
    ]

    all_findings = [f for r in results for f in r.findings]
    critical = [f for f in all_findings if f.severity == "CRITICAL"]
    warnings = [f for f in all_findings if f.severity == "WARNING"]
    info = [f for f in all_findings if f.severity == "INFO"]
    passed = [r for r in results if not r.critical and not r.warnings]

    lines += [
        "## Summary",
        f"- Critical: {len(critical)}",
        f"- Warning:  {len(warnings)}",
        f"- Info:     {len(info)}",
        f"- Clean:    {len(passed)}/{len(results)} skills",
        "",
    ]

    if critical:
        lines.append("## CRITICAL")
        lines.append("─" * 65)
        for f in critical:
            lines.append(f"**{f.skill}** | {f.check}")
            lines.append(f"  Detail: {f.detail}")
            if f.fix:
                lines.append(f"  Fix:    {f.fix}")
            lines.append("")

    if warnings:
        lines.append("## WARNING")
        lines.append("─" * 65)
        for f in warnings:
            lines.append(f"**{f.skill}** | {f.check}")
            lines.append(f"  Detail: {f.detail}")
            if f.fix:
                lines.append(f"  Fix:    {f.fix}")
            lines.append("")

    if info:
        lines.append("## INFO")
        lines.append("─" * 65)
        for f in info:
            lines.append(f"**{f.skill}** | {f.check}")
            lines.append(f"  Detail: {f.detail}")
            if f.fix:
                lines.append(f"  Fix:    {f.fix}")
            lines.append("")

    if passed:
        lines.append("## Clean Skills")
        lines.append("─" * 65)
        for r in passed:
            lines.append(f"  ✓ {r.skill}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit HVS skill library for drift")
    parser.add_argument("--skills-dir", help="Directory containing all user skills")
    parser.add_argument("--single", help="Audit a single skill directory")
    parser.add_argument("--standard", help="Path to hvs-system-standard.md (for reference)")
    parser.add_argument("--output", help="Write report to this file (default: stdout)")
    args = parser.parse_args()

    if not args.skills_dir and not args.single:
        parser.print_help()
        sys.exit(1)

    skill_dirs = []
    if args.single:
        skill_dirs.append(Path(args.single))
    else:
        skills_dir = Path(args.skills_dir)
        if not skills_dir.exists():
            print(f"ERROR: skills directory not found: {skills_dir}", file=sys.stderr)
            sys.exit(1)
        skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])

    results = [audit_skill(d) for d in skill_dirs]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = format_report(results, timestamp)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to: {args.output}")
    else:
        print(report)

    # Exit non-zero if critical findings
    all_critical = [f for r in results for f in r.critical]
    sys.exit(1 if all_critical else 0)


if __name__ == "__main__":
    main()
