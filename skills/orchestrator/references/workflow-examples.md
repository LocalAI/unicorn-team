# Orchestrator Workflow Examples

Step-by-step execution traces showing how the orchestrator runs each pipeline.
These are not descriptions — they show the exact sequence of actions, gates,
and decisions.

---

## Trace 1: Simple Feature — Add CSV Export Endpoint

**Classification:** SIMPLE-FEATURE (single domain, < 200 lines)

```
USER: "Add a CSV export endpoint for the reports API"

STEP 1 — Classify: Single endpoint, one domain → SIMPLE-FEATURE pipeline

STEP 2 — ACTION 1: Spawn Developer
  subagent_type: unicorn-team:developer
  prompt: "Implement CSV export endpoint GET /api/reports/{id}/csv.
    Context: existing reports API at src/api/reports.py, report model
    at src/models/report.py. Write the failing test FIRST. Coverage >= 80%.
    Return: summary, files, test results, coverage."

STEP 3 — Developer returns:
  summary: "Added CSV export endpoint with streaming response"
  files: src/api/reports.py, tests/test_reports_csv.py
  tests: 6 passed, 0 failed
  coverage: 88%

STEP 4 — GATE check:
  ✓ Tests pass (6/6)
  ✓ Coverage 88% >= 80%
  ✓ Self-review done
  ✓ No TODO/FIXME/HACK

STEP 5 — Return to user:
  ## Summary
  Added CSV export endpoint...
  ## Changes Made
  - src/api/reports.py: Added GET /api/reports/{id}/csv
  - tests/test_reports_csv.py: 6 tests for CSV export
  ## Tests
  - 6 tests added, coverage 88%, all passing
  ## Quality Gates
  - [x] All gates passed
```

---

## Trace 2: Complex Feature — Real-time Notifications

**Classification:** COMPLEX-FEATURE (multi-domain, needs design)

```
USER: "Add real-time push notifications for order status updates"

STEP 1 — Classify: Multi-service (orders + notifications + WebSocket),
  needs architecture → COMPLEX-FEATURE pipeline

STEP 2 — ACTION 1: Spawn Architect
  subagent_type: unicorn-team:architect
  prompt: "Design real-time notification system for order status updates.
    Context: order service at src/orders/, no existing WebSocket infra.
    Evaluate: WebSocket vs SSE vs polling. Produce ADR, message schema,
    implementation guide."

STEP 3 — Architect returns:
  ADR: docs/adr/ADR-015-realtime-notifications.md
  Decision: WebSocket with Redis pub/sub for horizontal scaling
  Schema: design-notifications/contracts/ws-messages.yaml
  Guide: design-notifications/implementation-guide.md

STEP 4 — GATE:
  ✓ ADR has 3 options evaluated (WebSocket, SSE, polling)
  ✓ Implementation guide present with phased plan
  ✓ Message schema defined

STEP 5 — ACTION 3: Spawn Developer
  subagent_type: unicorn-team:developer
  prompt: "Implement real-time notifications per design at
    design-notifications/. Key decision: WebSocket + Redis pub/sub.
    TDD — write the failing test FIRST. Coverage >= 80%."

STEP 6 — Developer returns:
  files: src/notifications/, src/orders/events.py, tests/test_notifications/
  tests: 14 passed, 0 failed, coverage 82%

STEP 7 — GATE:
  ✓ All tests pass
  ✓ Coverage 82% >= 80%
  ✓ Self-review done
  ✓ No markers

STEP 8 — ACTION 5: Spawn QA
  subagent_type: unicorn-team:qa-security
  prompt: "Review real-time notification implementation.
    Design: design-notifications/. Code: src/notifications/, src/orders/events.py.
    Focus: WebSocket auth, message injection, connection handling,
    Redis pub/sub security."

STEP 9 — QA returns:
  REJECTED — 1 high finding:
  "WebSocket connections not authenticated after initial handshake.
   src/notifications/ws_handler.py:45 — missing per-message token validation."

STEP 10 — GATE FAILED. Re-delegate to Developer:
  subagent_type: unicorn-team:developer
  prompt: "Fix QA finding: WebSocket connections need per-message auth.
    File: src/notifications/ws_handler.py:45. Add token validation on
    each incoming message, not just handshake. Write failing test first."

STEP 11 — Developer returns with fix. Re-run QA.

STEP 12 — QA returns: APPROVED (high finding resolved, 1 low noted).

STEP 13 — GATE: ✓ Approved

STEP 14 — Return to user with full Response Format.
```

---

## Trace 3: Parallel Delegation — Monitoring Stack

**Classification:** PARALLEL (3 independent services)

```
USER: "Set up monitoring for auth, billing, and notification services"

STEP 1 — Classify: Infrastructure task, 3 independent services
  → PARALLEL pipeline

STEP 2 — ACTION 1: Decompose into independent units:
  - Unit A: auth-service monitoring → DevOps
  - Unit B: billing-service monitoring → DevOps
  - Unit C: notification-service monitoring → DevOps
  - Unit D: shared Grafana overview dashboard → DevOps

  Wait — Units A/B/C are independent but Unit D depends on all three.
  → Parallel: A + B + C, then sequential: D

STEP 3 — ACTION 2: Spawn 3 agents in ONE message:

  Agent call #1:
    subagent_type: unicorn-team:devops
    description: "Auth service monitoring"
    prompt: "Set up Prometheus metrics, health checks, and structured
      logging for auth-service at services/auth/..."

  Agent call #2:
    subagent_type: unicorn-team:devops
    description: "Billing service monitoring"
    prompt: "Set up Prometheus metrics, health checks, and structured
      logging for billing-service at services/billing/..."

  Agent call #3:
    subagent_type: unicorn-team:devops
    description: "Notification service monitoring"
    prompt: "Set up Prometheus metrics, health checks, and structured
      logging for notification-service at services/notification/..."

  [All three execute concurrently]

STEP 4 — All three return. GATE each:
  Agent #1: ✓ IaC present, ✓ health checks, ✓ rollback docs
  Agent #2: ✓ IaC present, ✓ health checks, ✓ rollback docs
  Agent #3: ✗ Missing rollback procedure

  → Re-delegate Agent #3 only: "Gate failed: rollback procedure missing.
    Add rollback steps for notification-service monitoring."

STEP 5 — Agent #3 re-delegation returns. GATE: ✓ All pass.

STEP 6 — Spawn DevOps for overview dashboard (depends on all three):
  subagent_type: unicorn-team:devops
  prompt: "Create shared Grafana dashboard aggregating metrics from
    auth, billing, and notification services. Config files at
    [paths from steps 3-5]."

STEP 7 — GATE: ✓

STEP 8 — Return to user.
```

---

## Trace 4: New Technology — First Rust Service

**Classification:** NEW-TECH (Polyglot → Developer)

```
USER: "Rewrite the hot-path encoder in Rust for performance"

STEP 1 — Classify: New language + implementation → NEW-TECH pipeline

STEP 2 — ACTION 1: Spawn Polyglot
  subagent_type: unicorn-team:polyglot
  prompt: "Learn Rust for this team. Current stack is Python.
    Focus on: FFI with Python (PyO3), error handling patterns,
    testing idioms, cargo project setup. Produce quick-reference."

STEP 3 — Polyglot returns:
  Reference: docs/rust-quick-reference.md
  Key patterns: PyO3 for FFI, Result<T,E> for errors, #[cfg(test)] modules

STEP 4 — ACTION 2: Spawn Developer (implementation needed)
  subagent_type: unicorn-team:developer
  prompt: "Rewrite encoder at src/encoder/core.py in Rust with PyO3 FFI.
    Reference: docs/rust-quick-reference.md. Follow Rust idioms from
    the reference. TDD — write the failing test FIRST.
    Maintain Python API compatibility. Coverage >= 80%."

STEP 5 — Developer returns:
  files: src/encoder-rs/src/lib.rs, src/encoder-rs/Cargo.toml,
         tests/test_encoder_rust.py (Python integration tests)
  tests: 12 passed, coverage 85%

STEP 6 — GATE: ✓ All pass

STEP 7 — Return to user.
```

---

## Trace 5: Gate Failure Escalation

**What happens when an agent fails the same gate 3 times.**

```
STEP N — Developer returns: coverage 65%
GATE: ✗ Coverage 65% < 80%

Re-delegate #1: "Increase coverage to >= 80%. Uncovered: error paths in X, Y."
Developer returns: coverage 72%
GATE: ✗ Coverage 72% < 80%

Re-delegate #2: "Still at 72%. Specifically add tests for: [list uncovered functions].
  Use parameterized tests to cover edge cases efficiently."
Developer returns: coverage 75%
GATE: ✗ Coverage 75% < 80%

ESCALATE TO USER:
  "Developer agent failed to reach 80% coverage after 3 attempts.
   Best result: 75%. Uncovered: [specific functions].
   Options:
   1. Accept 75% coverage for this PR, track as tech debt
   2. I'll try a different approach (break into smaller units)
   3. You provide guidance on which paths to prioritize"
```
