# Delegation Examples

Concrete examples showing exact Agent tool call structure for each pipeline.
Each example shows the full chain of calls, not just one delegation.

---

## Example 1: Complex Feature — JWT Authentication

**Pipeline:** COMPLEX-FEATURE (Architect → Developer → QA)

### ACTION 1: Spawn Architect

```
Agent tool call:
  subagent_type: architect
  description: "Design JWT auth system"
  prompt: |
    Task: Design JWT authentication for a multi-tenant SaaS application.
    Must support SSO (SAML 2.0 + OIDC), per-tenant password policies,
    and API key management.

    Context:
    - Existing monolith at src/app/ being decomposed into services
    - Current auth is session-based, stored in PostgreSQL
    - 200+ enterprise tenants, some require HIPAA compliance

    Constraints:
    - Backward compatibility with session auth during migration
    - Latency: < 50ms for token validation
    - No vendor lock-in
    - HIPAA audit logging for healthcare tenants

    Expected output:
    - ADR at docs/adr/ADR-NNN-jwt-auth.md with alternatives evaluated
    - Sequence diagram for auth flows
    - OpenAPI spec for auth service
    - Implementation guide for Developer agent
    - Return: file paths to all artifacts, key decisions summary
```

### GATE CHECK after Architect returns:
- ADR has multiple options evaluated? ✓
- Implementation guide present? ✓
- API contract defined? ✓

### ACTION 3: Spawn Developer

```
Agent tool call:
  subagent_type: developer
  description: "Implement JWT auth with TDD"
  prompt: |
    Task: Implement JWT authentication service following the architecture design.

    Context:
    - Design: docs/adr/ADR-012-jwt-auth.md
    - API contract: design-auth/contracts/auth-api.yaml
    - Implementation guide: design-auth/implementation-guide.md
    - Key decisions: JWT with RS256, refresh token rotation, Redis token blacklist

    Constraints:
    - TDD required. Write the failing test FIRST. Do not write implementation
      code until the test exists and fails.
    - Coverage >= 80%
    - Match the OpenAPI spec exactly
    - HIPAA audit logging on all auth events

    Expected output:
    - Source files with paths listed
    - Test results (passed count, failed count)
    - Coverage percentage
    - Self-verification completed
```

### GATE CHECK after Developer returns:
- Tests pass? ✓
- Coverage >= 80%? ✓ (87%)
- Self-review done? ✓
- No TODO/FIXME? ✓

### ACTION 5: Spawn QA

```
Agent tool call:
  subagent_type: qa-security
  description: "Security review JWT auth"
  prompt: |
    Task: Security review of JWT authentication implementation.

    Context:
    - Design: docs/adr/ADR-012-jwt-auth.md
    - Implementation: src/auth/ (new service)
    - Tests: tests/test_auth/ (all passing, 87% coverage)

    Constraints:
    - 4-layer review: automated, logic, design, security
    - Security focus: token handling, key management, session fixation,
      CSRF, timing attacks on token validation
    - Verify HIPAA audit logging completeness
    - Check webhook signature validation

    Expected output:
    - Approval or rejection
    - Findings by severity (critical/high/medium/low)
    - Specific file:line references for each finding
    - Recommended fix for each finding
```

### GATE CHECK after QA returns:
- Approved? ✓ (with 2 medium findings noted for follow-up)

### Return to user with Response Format.

---

## Example 2: Bug Fix — Login Failure After Password Reset

**Pipeline:** BUG-FIX (Developer only)

### ACTION 1: Spawn Developer

```
Agent tool call:
  subagent_type: developer
  description: "Fix post-reset login bug"
  prompt: |
    Task: Debug and fix: users cannot log in after password reset.

    Context:
    - Password reset flow: src/auth/reset.py
    - Login flow: src/auth/login.py
    - User model: src/models/user.py
    - Recent change: password hashing was updated in commit abc123

    Constraints:
    - Use root-cause protocol:
      1. Write a failing test that reproduces the bug
      2. Form hypothesis about root cause
      3. Fix the root cause (not the symptom)
      4. Verify the failing test now passes
      5. Run full test suite — no regressions
    - Write the failing test FIRST. Do not write implementation code
      until the test exists and fails.
    - Coverage >= 80%

    Expected output:
    - Root cause explanation
    - Fix summary
    - Files changed with paths
    - Test results (passed, failed, coverage)
```

### GATE CHECK:
- Tests pass? ✓
- Coverage >= 80%? ✓
- Root cause identified? ✓

### Return to user.

---

## Example 3: Parallel — Backend + Frontend + Pipeline

**Pipeline:** PARALLEL (with sequential Architect prefix)

### ACTION 1: Spawn Architect (sequential — others depend on this)

```
Agent tool call:
  subagent_type: architect
  description: "Design user dashboard feature"
  prompt: |
    Task: Design the user dashboard feature. API contract needed for
    frontend/backend alignment.

    Context:
    - Existing API patterns at src/api/
    - Frontend at frontend/src/

    Constraints:
    - REST API with cursor pagination
    - Real-time updates via WebSocket

    Expected output:
    - ADR, OpenAPI spec, WebSocket message schema
    - Return file paths to all artifacts
```

### GATE: Design artifacts present? ✓

### ACTION 2: Spawn three agents IN ONE MESSAGE (parallel — independent)

```
Agent tool call #1:
  subagent_type: developer
  description: "Implement dashboard backend"
  prompt: |
    Task: Implement dashboard REST API and WebSocket handlers.
    Context: API spec at design-dashboard/contracts/api.yaml
    Constraints: TDD. Write the failing test FIRST. Coverage >= 80%.
    Expected output: files, test results, coverage.

Agent tool call #2:
  subagent_type: developer
  description: "Implement dashboard frontend"
  prompt: |
    Task: Implement dashboard UI components and WebSocket client.
    Context: API spec at design-dashboard/contracts/api.yaml
    Constraints: TDD. Write the failing test FIRST. Coverage >= 80%.
    Expected output: files, test results, coverage.

Agent tool call #3:
  subagent_type: devops
  description: "Set up dashboard pipeline"
  prompt: |
    Task: Add CI pipeline stage for dashboard service. WebSocket
    health checks, deployment config.
    Context: Existing pipeline at .github/workflows/ci.yml
    Constraints: IaC only, include rollback procedure.
    Expected output: pipeline config, deployment manifest, rollback docs.
```

All three return. GATE each independently.

### ACTION 4: Spawn QA for integration review

```
Agent tool call:
  subagent_type: qa-security
  description: "Review dashboard integration"
  prompt: |
    Task: Review combined dashboard implementation.
    Context:
    - Backend: src/api/dashboard/ (from parallel agent 1)
    - Frontend: frontend/src/dashboard/ (from parallel agent 2)
    - Pipeline: .github/workflows/ (from parallel agent 3)
    Constraints: 4-layer review. Focus on API contract alignment
    between frontend and backend.
    Expected output: approval/rejection, findings.
```

### GATE: QA approved? ✓

### Return to user.

---

## Example 4: Gate Failure and Re-delegation

**Showing what happens when a gate fails.**

### Developer returns with 65% coverage (gate requires 80%)

```
GATE FAILED: Coverage 65% < 80% required.

Re-delegate to Developer:

Agent tool call:
  subagent_type: developer
  description: "Add tests for coverage gap"
  prompt: |
    Task: Increase test coverage from 65% to >= 80%.

    Context:
    - Implementation at src/reports/generator.py (already complete)
    - Current tests at tests/test_reports.py (65% coverage)
    - Uncovered paths: error handling in generate_pdf(),
      edge cases in CSV export for empty datasets

    Constraints:
    - Write the failing test FIRST.
    - Target >= 80% coverage
    - Do not change implementation unless tests reveal bugs

    Expected output:
    - Updated test file paths
    - New coverage percentage
    - Test results
```

Developer returns with 84% coverage. GATE passes. Continue pipeline.
