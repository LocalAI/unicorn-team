# Pipeline Definitions

Detailed ACTION sequences for each pipeline. The orchestrator references
these after classification (Step 1). Every pipeline that produces code
includes mandatory Test Engineer verification and QA-Security review.

## Mandatory Post-Code Steps

**After ANY pipeline action that produces code changes**, these steps run
automatically before the pipeline returns. They are NOT optional.

```
TEST VERIFICATION: Spawn test-engineer
  → "Review tests written for this change. Verify:
     - Tests cover all acceptance criteria and edge cases
     - No test gaps (code paths without coverage)
     - Tests verify behavior, not implementation details
     - Coverage meets threshold (80% line, 70% branch)
     Return: TESTS_SUFFICIENT or TESTS_INSUFFICIENT with missing cases."
  GATE: TESTS_SUFFICIENT? YES → continue. NO → Spawn Developer to add
  missing tests, then re-verify (max 2 iterations).

SECURITY REVIEW: Spawn qa-security
  → "Security review of changed files. Check:
     - Input validation on all external data
     - No hardcoded secrets or credentials
     - Auth/authz properly enforced
     - OWASP Top 10 vulnerabilities
     - Safe error handling (no info leakage)
     Return: SECURE or SECURITY_ISSUES with file:line fixes."
  GATE: SECURE? YES → continue. NO → Spawn Developer to fix,
  then re-review (max 2 iterations).
```

These steps are referenced as `→ MANDATORY: Test Verification + Security Review`
in the pipeline definitions below.

---

## Pipeline: SIMPLE-FEATURE

**When:** Single-domain feature, < 200 lines of new code.

```
ACTION 1: Spawn Developer agent
  → subagent_type: unicorn-team:developer
  → prompt: Include task, context (file paths), constraints, and:
    "Write the failing test FIRST (RED), then implement (GREEN),
     then refactor (REFACTOR). Run self-verification before returning.
     Return: summary, files changed, test results, coverage."

ACTION 2: GATE — Check Developer result
  → Tests pass?           YES → continue    NO → Re-delegate with failure details
  → Coverage >= 80%?      YES → continue    NO → Re-delegate asking for more tests
  → Self-review done?     YES → continue    NO → Re-delegate requesting self-review
  → No TODO/FIXME/HACK?   YES → continue    NO → Re-delegate requesting cleanup

ACTION 3: → MANDATORY: Test Verification + Security Review

ACTION 4: Return to user using Response Format
```

---

## Pipeline: COMPLEX-FEATURE

**When:** Multi-domain feature, > 200 lines, needs design before code.

```
ACTION 1: Spawn Architect agent
  → subagent_type: unicorn-team:architect
  → prompt: "Design [feature]. Produce: ADR, API contract (if applicable),
    data model (if applicable), implementation guide for Developer.
    Return: file paths to all design artifacts."

ACTION 2: GATE — Check Architect result
  → ADR exists with alternatives evaluated?  YES → continue   NO → Re-delegate
  → Implementation guide present?            YES → continue   NO → Re-delegate

ACTION 3: Spawn Developer agent
  → subagent_type: unicorn-team:developer
  → prompt: "Implement [feature] following the design at [paths from ACTION 1].
    Key decisions: [list from ADR]. TDD required — failing test first.
    Return: summary, files changed, test results, coverage."

ACTION 4: GATE — Check Developer result (same gates as SIMPLE-FEATURE ACTION 2)

ACTION 5: → MANDATORY: Test Verification + Security Review

ACTION 6: Spawn QA agent (full 4-layer review)
  → subagent_type: unicorn-team:qa-security
  → prompt: "Review implementation of [feature].
    Design: [paths from ACTION 1]. Code: [paths from ACTION 3].
    Run FULL 4-layer review: automated, logic, design, security.
    Return: approval or rejection with specific findings."

ACTION 7: GATE — Check QA result
  → Approved?                        YES → continue
  → Rejected with fixable issues?    → Spawn Developer with QA feedback, then re-run QA
  → Rejected with design issues?     → Spawn Architect with QA feedback, restart from ACTION 3

ACTION 8: Return to user using Response Format
```

---

## Pipeline: BUG-FIX

**When:** Something is broken and needs fixing.

```
ACTION 1: Spawn Developer agent
  → subagent_type: unicorn-team:developer
  → prompt: "Debug and fix: [bug description].
    Use root-cause protocol:
    1. Write a failing test that reproduces the bug
    2. Form hypothesis about root cause
    3. Fix the root cause (not the symptom)
    4. Verify the failing test now passes
    5. Check for similar bugs nearby
    6. Run full test suite — no regressions
    Return: root cause, fix summary, files changed, test results."

ACTION 2: GATE — Check Developer result (same gates as SIMPLE-FEATURE ACTION 2)

ACTION 3: → MANDATORY: Test Verification + Security Review

ACTION 4: Return to user using Response Format
```

---

## Pipeline: ARCHITECTURE

**When:** Design decision, system design, or tradeoff analysis needed.

```
ACTION 1: Spawn Architect agent
  → subagent_type: unicorn-team:architect
  → prompt: "Design [system/decision]. Evaluate multiple options.
    Produce ADR with tradeoff analysis, diagrams, and implementation guide.
    Include STRIDE threat model for security-critical decisions.
    Return: file paths to all design artifacts, key decision summary."

ACTION 2: GATE — Check Architect result
  → Multiple options evaluated?    YES → continue   NO → Re-delegate
  → Tradeoffs explicit?            YES → continue   NO → Re-delegate
  → Implementation guidance given? YES → continue   NO → Re-delegate

ACTION 3: Return to user using Response Format
```

---

## Pipeline: REVIEW

**When:** Code review, PR review, or security audit.

```
ACTION 1: Spawn QA agent
  → subagent_type: unicorn-team:qa-security
  → prompt: "Review [target]. Apply 4-layer review:
    Layer 1: Automated (tests, coverage, linting)
    Layer 2: Logic (correctness, edge cases, error handling)
    Layer 3: Design (SRP, complexity, coupling)
    Layer 4: Security (inputs, auth, data handling, OWASP Top 10)
    Return: approval/rejection, findings by severity, specific file:line references."

ACTION 2: Return to user using Response Format
```

---

## Pipeline: DEPLOY

**When:** CI/CD, infrastructure, deployment, or monitoring.

```
ACTION 1: Spawn DevOps agent
  → subagent_type: unicorn-team:devops
  → prompt: "[deployment task]. Include:
    - Infrastructure as code (not ClickOps)
    - Health checks and rollback procedures
    - Security hardening
    Return: files created, deployment steps, rollback procedure."

ACTION 2: GATE — Check DevOps result
  → IaC files present (not manual steps)?  YES → continue   NO → Re-delegate
  → Rollback procedure documented?         YES → continue   NO → Re-delegate

ACTION 3: Spawn QA agent (infrastructure security review)
  → subagent_type: unicorn-team:qa-security
  → prompt: "Security review of infrastructure changes.
    Files: [IaC files from ACTION 1]. Check:
    - IAM permissions follow least privilege
    - No public exposure of internal services
    - Secrets managed via Secrets Manager (not env vars)
    - TLS/encryption enabled where applicable
    - Network security (VPC, security groups, NACLs)
    Return: SECURE or SECURITY_ISSUES with specific fixes."

ACTION 4: GATE — Check QA result
  → SECURE? YES → continue. NO → Spawn DevOps with fixes, re-review.

ACTION 5: Return to user using Response Format
```

---

## Pipeline: NEW-TECH

**When:** Learning a new language, framework, or technology.

```
ACTION 1: Spawn Polyglot agent
  → subagent_type: unicorn-team:polyglot
  → prompt: "Learn [technology]. Produce quick-reference with:
    - Key concepts mapped to familiar equivalents
    - Idiomatic patterns (not transliterated code)
    - Tooling setup (build, test, lint, format)
    - Common pitfalls and SECURITY considerations
    Return: reference document path, key patterns summary."

ACTION 2: IF implementation is also needed:
  Spawn Developer agent
  → subagent_type: unicorn-team:developer
  → prompt: "Implement [feature] in [technology].
    Reference: [path from ACTION 1].
    Follow idiomatic patterns from the reference. TDD required.
    Return: summary, files changed, test results, coverage."

ACTION 3: GATE — Check Developer result (if ACTION 2 ran)

ACTION 4: IF ACTION 2 ran → MANDATORY: Test Verification + Security Review

ACTION 5: Return to user using Response Format
```

---

## Pipeline: AI-FEATURE

**When:** AI/ML implementation, LLM integration, agent development, prompt engineering,
recommendation systems, or intelligent automation.

```
ACTION 1: Spawn Architect agent
  → subagent_type: unicorn-team:architect
  → prompt: "Design [AI feature]. Consider:
    - Model selection (cost, latency, capability tradeoffs)
    - Token management and context window strategy
    - Prompt design and response handling
    - Fallback and error handling for model failures
    - Data flow: input preprocessing → model → output postprocessing
    Produce ADR and implementation guide."

ACTION 2: GATE — Check Architect result
  → ADR with model selection rationale?  YES → continue   NO → Re-delegate
  → Implementation guide present?        YES → continue   NO → Re-delegate

ACTION 3: Spawn AI Engineer agent
  → subagent_type: ai-engineer:ai-engineer
  → prompt: "Implement [AI feature] following design at [paths from ACTION 1].
    TDD required. Include:
    - Model integration with proper error handling
    - Token counting and context management
    - Response streaming if applicable
    - Fallback behavior when model is unavailable
    Return: summary, files changed, test results, coverage."

ACTION 4: GATE — Check AI Engineer result (same gates as Developer)

ACTION 5: → MANDATORY: Test Verification + Security Review

ACTION 6: Spawn QA agent (full 4-layer review)
  → subagent_type: unicorn-team:qa-security
  → prompt: "Review AI feature implementation.
    Design: [paths from ACTION 1]. Code: [paths from ACTION 3].
    Additional focus: prompt injection risks, data leakage, model output
    validation, cost controls, rate limiting.
    Run FULL 4-layer review. Return: approval or rejection."

ACTION 7: GATE — Check QA result (same as COMPLEX-FEATURE)

ACTION 8: Return to user using Response Format
```

---

## Pipeline: PARALLEL

**When:** Task decomposes into 2+ independent sub-tasks that don't depend on
each other's output.

```
ACTION 1: Decompose the task into independent units.
  List them explicitly:
    - Unit A: [description] → [agent type]
    - Unit B: [description] → [agent type]
    - Unit C: [description] → [agent type]

ACTION 2: Spawn ALL independent agents in ONE message.
  ┌─────────────────────────────────────────────────────┐
  │ CRITICAL: Use multiple Agent tool calls in a SINGLE │
  │ response message. This is how parallel execution    │
  │ works — multiple tool calls, one message.           │
  └─────────────────────────────────────────────────────┘
  Each Agent call gets its own:
  → subagent_type, prompt, description

ACTION 3: GATE — Check ALL results before proceeding.
  All passed? → continue
  Some failed? → Re-delegate only the failed units

ACTION 4: → MANDATORY: Test Verification + Security Review (on combined changes)

ACTION 5: Spawn QA agent to review the combined result (integration review)
  → subagent_type: unicorn-team:qa-security
  → prompt: "Integration review of parallel implementation.
    Units: [list]. Combined files: [all changed files].
    Check: cross-unit integration, shared state consistency, security.
    Run FULL 4-layer review. Return: approval or rejection."

ACTION 6: GATE — Check QA result

ACTION 7: Return to user using Response Format
```

**Parallel + Sequential Hybrid Example:**
```
Architect produces design (sequential — others depend on it)
    ↓
Developer (backend) + Developer (frontend) + DevOps (pipeline)
    ↓  (all three in ONE message — they're independent)
Test Verification + Security Review (on combined changes)
    ↓
QA reviews combined result (sequential — depends on all)
```
