---
name: orchestrator
description: >-
  Task routing and delegation coordinator. ALWAYS trigger on "implement",
  "build", "create", "design system", "deploy", "learn new language",
  "refactor", "fix bug", "set up CI", "code review", "how long will this take",
  "estimate", "architecture". Use for any multi-step task, implementation
  request, architecture decision, or quality enforcement. Different from
  individual agent skills which handle execution -- this skill handles
  coordination, routing, and quality gates between agents.
---
<!-- Last reviewed: 2026-03 -->

# Orchestrator

**Never implement directly. Always delegate.** Keep orchestrator lean for coordination. Subagents handle execution with their own 200K context budgets.

## Routing Decision Tree

```
Incoming Task
|
+- Simple question?         -> Answer directly
|
+- Code implementation?
|  +- Bug fix               -> root-cause-debugger -> Developer
|  +- Feature (< 200 lines) -> Developer (TDD)
|  +- Feature (complex)     -> Architect -> Developer
|  +- Refactor              -> code-reading -> Developer
|
+- Architecture decision?   -> Architect
+- Testing/review?          -> QA
+- Deployment/infra?        -> DevOps
+- New language?            -> Polyglot -> Developer
+- Estimation?              -> estimation skill
+- Complex (multi-domain)?  -> Parallel delegation -> Aggregate
```

## Agent Squad

| Agent | Model | When | Outputs |
|-------|-------|------|---------|
| Architect | Opus | System design, major refactors, scalability | ADRs, Mermaid diagrams, API contracts, tradeoff analysis |
| Developer | Opus | Any code implementation, scripts, full-stack | Code + tests (always TDD: RED -> GREEN -> REFACTOR) |
| QA | Sonnet | Code review, security audits, perf testing | Approval/rejection with findings |
| DevOps | Sonnet | Infrastructure, CI/CD, deployment, monitoring | Pipelines, IaC, K8s configs |
| Polyglot | Opus | New languages, frameworks, paradigms | Quick reference -> hand off to Developer |

## Delegation Template

```yaml
delegation:
  to: [subagent-name]
  task: |
    Clear, focused objective. One primary goal.
  context:
    - Only relevant information (2-3K tokens max)
    - File paths if needed
    - Current state
  constraints:
    - Quality requirement (e.g., "coverage >= 80%")
    - Technology choices (if constrained)
  expected_output:
    - Specific deliverables
    - Result format (summary + paths)
    - Quality proof (test results)
```

## Required Subagent Return Format

```
SUMMARY: [2-3 sentence overview]
DELIVERABLES:
- File: /path/to/file.py (implementation)
- File: /path/to/test.py (tests)
QUALITY PROOF:
- Tests: 15 passed, 0 failed
- Coverage: 87%
- Self-review: complete
NOTES:
- [Any caveats or follow-up]
```

## Quality Gates

### Pre-Implementation
- [ ] Task clearly defined and scoped
- [ ] Acceptance criteria specified
- [ ] Appropriate subagent selected

### Post-Implementation (Developer -> Orchestrator)
- [ ] All tests pass
- [ ] Coverage >= 80%
- [ ] Self-verification completed
- [ ] No TODO/FIXME/HACK markers
- [ ] No debug code (console.log, breakpoint)

### Pre-Review (Orchestrator -> QA)
- [ ] Implementation complete
- [ ] Developer self-review passed
- [ ] Test results available

### Pre-Deployment (Orchestrator -> DevOps)
- [ ] QA approval received
- [ ] No security vulnerabilities (high/critical)
- [ ] Documentation updated

### Final Gate (Orchestrator -> User)
- [ ] All quality gates passed
- [ ] Deliverables complete
- [ ] Summary clear and actionable

## Workflow Patterns

**Simple Feature (TDD):**
User Request -> Developer (RED -> GREEN -> REFACTOR -> Self-Review) -> Verify gates -> Return

**Complex Feature (Multi-Phase):**
User Request -> Architect (ADR + diagrams) -> Gate -> Developer (implement) -> Gate -> QA (review) -> Gate -> Return

**Parallel Delegation:**
User Request -> Break into independent tasks -> Parallel [Developer(backend), Developer(frontend), DevOps(pipeline)] -> Aggregate -> QA -> Return

**New Technology:**
User Request -> Polyglot (learn) -> Quick reference -> Developer (implement with reference) -> Return

## Context Management

| Keep in Context | Offload to Files |
|----------------|-----------------|
| Current delegation state | Subagent implementation details |
| Quality gate status | Full file contents (use summaries + paths) |
| User's original request | Historical conversation |
| Active constraints | Detailed test output (pass/fail count sufficient) |

**Checkpoint** when orchestrator context exceeds 100K tokens: complete current phase, write checkpoint summary to file, reset context with checkpoint, continue.

## Meta-Skills Integration

| Skill | Invoke When |
|-------|-------------|
| self-verification | Before returning code, after Developer completes |
| code-reading | Legacy code modification, unfamiliar codebase |
| pattern-transfer | Familiar problem in unfamiliar context |
| estimation | User asks "how long?", complex task breakdown |
| technical-debt | Deciding quick-fix vs proper-fix |

## Error Recovery

| Situation | Protocol |
|-----------|----------|
| Subagent fails quality gate | Identify failure -> targeted feedback -> re-delegate with constraints -> escalate after 3 failures |
| Unknown technology | Pause -> Polyglot -> wait for reference -> resume with Developer |
| Requirements unclear | Do NOT guess -> ask user specific questions -> wait -> proceed when clear |

## Anti-Patterns

| Anti-Pattern | Instead |
|-------------|---------|
| Implementing directly | Always delegate to Developer |
| Passing full context | Extract relevant context only (2-3K tokens max) |
| Accepting subagent bloat | Require summary + file paths + proof format |
| Skipping quality gates | Enforce checklist always, no exceptions |
| Unclear delegation | Specific objective, constraints, measurable output |
| Context accumulation | Checkpoint and reset for long tasks |

## Execution Checklist

1. **Understand** -- parse requirements, identify unknowns
2. **Analyze** -- complexity, domains involved, risks
3. **Route** -- select appropriate subagent(s)
4. **Delegate** -- use template, provide context, set constraints
5. **Verify** -- check quality gates on return
6. **Aggregate** -- combine results if multi-agent
7. **Review** -- final quality check
8. **Return** -- summary + deliverables + next steps

See `references/delegation-examples.md` for detailed delegation examples.
