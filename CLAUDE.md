# 10X Developer Unicorn

Complete agent orchestration system for Claude Code.

## Status: COMPLETE

All 6 phases implemented. 80+ tests passing. Skills reworked to official Anthropic patterns (2026-03).

## Project Overview

This project creates a comprehensive agent orchestration system with:
- Specialized subagents (Architect, Developer, QA, DevOps, Polyglot)
- Skills matrix (core, domain, meta)
- Quality enforcement (hooks, scripts, gates)
- TDD-first development workflow

Model Strategy: Opus everywhere for consistency and quality.

## Quick Start

```bash
./scripts/install.sh
pytest tests/ -v
```

## Architecture Reference

- `docs/architecture.md` - Agent specs, workflows, token management
- `docs/hidden-skills.md` - The 80% skills (code reading, pattern transfer, etc.)
- `docs/implementation-guide.md` - Directory structure, quickstart
- `SYSTEM_PROMPT.md` - Copy to ~/.claude/CLAUDE.md to activate

## Project Structure

```
unicorn-team/
├── CLAUDE.md
├── SYSTEM_PROMPT.md
├── README.md
├── docs/
│   ├── architecture.md
│   ├── hidden-skills.md
│   ├── implementation-guide.md
│   └── TROUBLESHOOTING.md
├── skills/
│   ├── unicorn/                       # Meta-skills (7)
│   │   ├── orchestrator/SKILL.md
│   │   ├── self-verification/
│   │   │   ├── SKILL.md
│   │   │   ├── references/
│   │   │   └── scripts/self-review.sh
│   │   ├── code-reading/SKILL.md
│   │   ├── pattern-transfer/SKILL.md
│   │   ├── estimation/
│   │   │   ├── SKILL.md
│   │   │   ├── references/
│   │   │   └── scripts/estimate.sh
│   │   ├── technical-debt/SKILL.md
│   │   └── language-learning/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── scripts/new-language.sh
│   ├── agents/                        # Agent definitions (5)
│   │   ├── developer/
│   │   │   ├── SKILL.md
│   │   │   ├── references/
│   │   │   └── scripts/tdd.sh
│   │   ├── architect/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   ├── qa-security/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   ├── devops/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   └── polyglot/
│   │       ├── SKILL.md
│   │       ├── references/
│   │       └── scripts/new-language.sh
│   └── domain/                        # Domain skills (5)
│       ├── python/
│       ├── javascript/
│       ├── testing/
│       ├── security/
│       └── devops/
├── hooks/
│   ├── pre-commit
│   └── pre-push
├── scripts/
│   └── install.sh
└── tests/
    ├── test_hooks.py
    ├── test_scripts.py
    └── test_skills_valid.py
```

## Development Rules

### TDD Always
```
RED: Write failing test first
GREEN: Minimum code to pass
REFACTOR: Improve without changing behavior
VERIFY: Self-review before commit
```

### Skill File Standards

Every SKILL.md must have:
```yaml
---
name: skill-name
description: >-
  Third-person description. ALWAYS trigger on "phrase1", "phrase2", "phrase3".
  Use when [conditions]. Different from [sibling] which [difference].
---
```

Body guidelines:
- Under 500 lines (target 150-300; split to references/ if larger)
- Action over explanation (Claude is already smart)
- Decision tables and checklists over prose
- Scripts co-located in skill's scripts/ directory
- Detailed content in references/ directory

### Quality Gates

Before any commit:
- Tests pass (pytest -v)
- Scripts are executable
- SKILL.md has valid frontmatter
- No TODO/FIXME/HACK markers
- Self-review checklist complete

### Commit Convention

```
type(scope): description

Types: feat, fix, docs, skill, script, test, refactor
Scope: orchestrator, developer, qa, devops, hooks, etc.
```

## Implementation Status

### Phase 1: Foundation - COMPLETE
- [x] Directory structure
- [x] skills/unicorn/orchestrator/SKILL.md
- [x] skills/unicorn/self-verification/SKILL.md
- [x] hooks/pre-commit
- [x] scripts/install.sh
- [x] Validation tests

### Phase 2: Core Skills - COMPLETE
- [x] skills/unicorn/code-reading/SKILL.md
- [x] skills/unicorn/pattern-transfer/SKILL.md
- [x] skills/unicorn/estimation/SKILL.md
- [x] skills/unicorn/technical-debt/SKILL.md
- [x] skills/unicorn/language-learning/SKILL.md

### Phase 3: Agent Definitions - COMPLETE
- [x] skills/agents/developer/SKILL.md + references/ + scripts/
- [x] skills/agents/architect/SKILL.md + references/
- [x] skills/agents/qa-security/SKILL.md + references/
- [x] skills/agents/devops/SKILL.md + references/
- [x] skills/agents/polyglot/SKILL.md + references/ + scripts/

### Phase 4: Domain Skills - COMPLETE
- [x] skills/domain/python/SKILL.md
- [x] skills/domain/javascript/SKILL.md
- [x] skills/domain/testing/SKILL.md
- [x] skills/domain/security/SKILL.md
- [x] skills/domain/devops/SKILL.md

### Phase 5: Scripts & Automation - COMPLETE
- [x] skills/agents/developer/scripts/tdd.sh (moved from scripts/)
- [x] skills/unicorn/self-verification/scripts/self-review.sh (moved from scripts/)
- [x] skills/unicorn/estimation/scripts/estimate.sh (moved from scripts/)
- [x] skills/unicorn/language-learning/scripts/new-language.sh (moved from scripts/)
- [x] hooks/pre-push

### Phase 6: Documentation & Polish - COMPLETE
- [x] README.md with Mermaid diagrams
- [x] SYSTEM_PROMPT.md for activation
- [x] docs/TROUBLESHOOTING.md
- [x] All skills refactored to <500 lines with references/

## Commands

```bash
./scripts/install.sh                                          # Install system
./skills/agents/developer/scripts/tdd.sh <feature>            # TDD workflow
./skills/unicorn/self-verification/scripts/self-review.sh     # Pre-commit checklist
./skills/unicorn/estimation/scripts/estimate.sh               # PERT estimation
./skills/unicorn/language-learning/scripts/new-language.sh <lang>  # Language learning
pytest tests/ -v                                              # Run all tests
```

## Token Management

- Keep orchestrator context lean (coordination only)
- Delegate heavy work to subagents (each gets 200K)
- Skills lazy-load (body only when triggered)
- Return summaries, not full outputs

## Delegation Routing

```
Simple question        -> Answer directly
Implementation         -> Developer subagent
Architecture decision  -> Architect subagent
Code review            -> QA subagent
Deployment             -> DevOps subagent
New language           -> Polyglot subagent
Complex multi-domain   -> Parallel delegation
```

## Success Criteria - ALL MET

### Functional
- [x] All skills have valid frontmatter
- [x] All scripts executable and tested
- [x] Pre-commit hook catches quality issues
- [x] TDD workflow enforces red-green-refactor
- [x] Self-review checklist integrated

### Quality
- [x] 80+ tests passing
- [x] No TODO/FIXME/HACK in committed code
- [x] All skills under 500 lines
- [x] Documentation complete

### Usability
- [x] Single-command installation
- [x] Clear error messages
- [x] Works with existing Claude Code setup
- [x] Non-destructive

## Repository

https://github.com/aj-geddes/unicorn-team
