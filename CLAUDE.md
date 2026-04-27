# 10X Developer Unicorn

Agent orchestration system for Claude Code. 6 agents + 16 skills, dual-layer
architecture where agents spawn as subprocesses with fresh context windows.

## Architecture: Agents + Skills

**Agents** (`agents/*.md`) are subprocess definitions spawned via the Agent
tool. Each gets a fresh context window. Agent protocol content is inlined
directly in the agent definition body to avoid registering as user-facing slash
commands. Agents live at the plugin root (`agents/`) so the plugin system
registers them; `.claude/agents` is a symlink for local dev compatibility.

**Skills** (`skills/*/SKILL.md`) are composable protocol documents (meta +
domain) that provide shared knowledge. All skills in `skills/` are
user-invocable.

**Protocols** (`.claude/protocols/`) contain reference materials and scripts
used by agents (not registered as skills).

| Agent (subagent_type) | Model | Composable Skills |
|-----------------------|-------|-------------------|
| `unicorn-team:developer` | sonnet | self-verification, testing, python, javascript, go |
| `unicorn-team:architect` | opus | pattern-transfer, code-reading, technical-debt |
| `unicorn-team:qa-security` | sonnet | security, testing |
| `unicorn-team:devops` | sonnet | domain-devops, security |
| `unicorn-team:polyglot` | opus | language-learning, pattern-transfer, code-reading |
| `unicorn-team:platform-docs` | opus | self-verification, code-reading, technical-debt |

The orchestrator is a **skill** (not an agent) that runs in the main context
and coordinates delegation to agents.

## Orchestrator Mode

You coordinate the 10X Unicorn agent team. Delegate all substantial work to
agents (Agent tool). Never implement complex tasks directly.

- Route tasks using the orchestrator skill's decision tree
- Enforce TDD: tests first, always (RED -> GREEN -> REFACTOR)
- Apply quality gates before returning results
- Each agent gets a fresh context window -- use it

The orchestrator skill (`skills/orchestrator/SKILL.md`) has the full
routing table, delegation templates, quality gates, and response format.

## Quick Start

```bash
# Add the marketplace and install
claude plugin marketplace add aj-geddes/unicorn-team
claude plugin install unicorn-team@unicorn-team
```

For development:
```bash
git clone https://github.com/aj-geddes/unicorn-team.git
cd unicorn-team
pytest tests/ -v            # Verify everything passes
```

## Development Rules

### TDD Always
```
RED:      Write failing test first
GREEN:    Minimum code to pass
REFACTOR: Improve without changing behavior
VERIFY:   Self-review before commit
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
- No unresolved task markers
- Self-review checklist complete

### Commit Convention

```
type(scope): description

Types: feat, fix, docs, skill, script, test, refactor
Scope: orchestrator, developer, qa, devops, hooks, etc.
```

## Commands

```bash
.claude/protocols/developer/scripts/tdd.sh <feature>          # TDD workflow
skills/self-verification/scripts/self-review.sh               # Pre-commit checklist
skills/estimation/scripts/estimate.sh                         # PERT estimation
skills/language-learning/scripts/new-language.sh <lang>       # Language learning
pytest tests/ -v                                              # Run all tests
./scripts/validate.sh                                         # Validate plugin structure
```

## Delegation Routing

```
Simple question        -> Answer directly
Implementation         -> unicorn-team:developer
AI/ML / LLM feature   -> ai-engineer:ai-engineer
Architecture decision  -> unicorn-team:architect
Code review            -> unicorn-team:qa-security
Test verification      -> test-engineer (automatic after every code change)
Security review        -> unicorn-team:qa-security (automatic after every code change)
Deployment             -> unicorn-team:devops
New language           -> unicorn-team:polyglot
Complex multi-domain   -> Parallel agent delegation
Platform docs / audit  -> unicorn-team:platform-docs
Execute plan           -> plan-runner skill
Performance            -> performance-optimizer
```

## Architecture Reference

- `docs/architecture.md` - Agent specs, workflows, delegation design
- `docs/skills.md` - All 16 skills, composition, and creation guide
- `docs/getting-started.md` - Installation and first task walkthrough

## Repository

https://github.com/aj-geddes/unicorn-team
