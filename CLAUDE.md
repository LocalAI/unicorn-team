# 10X Developer Unicorn

Complete agent orchestration system for Claude Code.

## Status: COMPLETE

All 6 phases implemented. 62 tests passing.

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
│   │   ├── self-verification/SKILL.md
│   │   ├── code-reading/SKILL.md
│   │   ├── pattern-transfer/SKILL.md
│   │   ├── estimation/SKILL.md
│   │   ├── technical-debt/SKILL.md
│   │   └── language-learning/
│   │       ├── SKILL.md
│   │       └── references/
│   ├── agents/                        # Agent definitions (5)
│   │   ├── developer.md
│   │   ├── architect.md
│   │   ├── qa-security.md
│   │   ├── devops.md
│   │   ├── polyglot.md
│   │   └── references/
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
│   ├── install.sh
│   ├── tdd.sh
│   ├── self-review.sh
│   ├── estimate.sh
│   └── new-language.sh
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
description: >
  Clear description of what it does AND when to use it.
  Include trigger phrases.
---
```

Body guidelines:
- Under 500 lines (split to references/ if larger)
- Imperative voice
- Concrete examples over explanations

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
- [x] skills/agents/developer.md
- [x] skills/agents/architect.md
- [x] skills/agents/qa-security.md
- [x] skills/agents/devops.md
- [x] skills/agents/polyglot.md

### Phase 4: Domain Skills - COMPLETE
- [x] skills/domain/python/SKILL.md
- [x] skills/domain/javascript/SKILL.md
- [x] skills/domain/testing/SKILL.md
- [x] skills/domain/security/SKILL.md
- [x] skills/domain/devops/SKILL.md

### Phase 5: Scripts & Automation - COMPLETE
- [x] scripts/tdd.sh
- [x] scripts/self-review.sh
- [x] scripts/estimate.sh
- [x] scripts/new-language.sh
- [x] hooks/pre-push

### Phase 6: Documentation & Polish - COMPLETE
- [x] README.md with Mermaid diagrams
- [x] SYSTEM_PROMPT.md for activation
- [x] docs/TROUBLESHOOTING.md
- [x] All skills refactored to <500 lines with references/

## Commands

```bash
./scripts/install.sh              # Install system
./scripts/tdd.sh <feature>        # TDD workflow
./scripts/self-review.sh          # Pre-commit checklist
./scripts/estimate.sh             # PERT estimation
./scripts/new-language.sh <lang>  # Language learning
pytest tests/ -v                  # Run all tests
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
- [x] 62 tests passing
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
