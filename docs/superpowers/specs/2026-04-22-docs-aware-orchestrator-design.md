# Docs-Aware Orchestrator — Design Spec

**Goal:** Make the unicorn-team orchestrator automatically inject architecture documentation context into every pipeline that targets a documented repo, and report docs-vs-code deviations after implementation completes.

**Approach:** Two cross-cutting steps (1.5 and 3) wrap around existing pipelines. No pipeline internals change. A two-tier context system (brief/deep) scales context size to pipeline complexity. Post-implementation deviation reports require user approval before writing docs changes.

---

## Architecture

### Current Flow

```
Step 1: Classify task → pick pipeline
Step 2: Execute pipeline (ACTION → GATE → ACTION → GATE → ...)
        Return to user
```

### New Flow

```
Step 1:   Classify task → pick pipeline
Step 1.5: Docs Context Enrichment (if target repo is in active manifest)
Step 2:   Execute pipeline (agents receive docs context in delegation prompts)
Step 3:   Docs Deviation Report (if Step 1.5 ran; user approves before writes)
          Return to user
```

Steps 1.5 and 3 are no-ops when:
- No platform-docs registry exists
- No active project is set
- The target repo is not in the active project's manifest
- The task doesn't target a specific repo (e.g., pure architecture questions)

### Triggering Conditions

The orchestrator determines the target repo by:
1. Checking if the user's working directory is within a manifest repo path
2. Checking if the user explicitly names a repo ("implement X in agentcore")
3. Checking if file paths in the request match a manifest repo path

If multiple repos are targeted (PARALLEL pipeline), each unit gets its own context enrichment.

---

## Step 1.5: Docs Context Enrichment

### Operation: `context-read`

New operation type for the platform-docs agent. Two tiers:

**Brief (~500 tokens):**
- Repo health from latest current-state report (or "no report" if none exists)
- Current phase name and approximate completion
- Critical technical constraints (gotchas that would break implementation)
- Active debt items affecting this repo

**Deep (~1500 tokens, includes brief):**
- Relevant phase implementation guide summary
- Applicable architecture patterns from the patterns directory
- Relevant ADR decisions with rationale
- Compliance checklist items for the current work area

### Tier Assignment

| Pipeline | Tier | Rationale |
|----------|------|-----------|
| SIMPLE-FEATURE | Brief | Constraints only; avoid overhead |
| COMPLEX-FEATURE | Deep | Architecture alignment needed for design |
| BUG-FIX | Brief | Root cause is in code; constraints prevent regressions |
| ARCHITECTURE | Deep | Must evaluate against existing decisions |
| REVIEW | Deep | QA needs architecture context for design-layer review |
| DEPLOY | Brief | Operational; constraints prevent misconfiguration |
| NEW-TECH | Brief | Technology choice, not architecture-dependent |
| PARALLEL | Per-unit | Each unit gets tier based on its sub-pipeline |

### Agent Delegation

The orchestrator spawns the platform-docs agent:

```
Agent tool call:
  subagent_type: unicorn-team:platform-docs
  description: "context-read (brief|deep) for [repo] — [project name]"
  prompt: |
    ## Operation
    Command: context-read
    Tier: brief | deep
    Target repo: [repo key]
    Task summary: [one-line summary of user's request]

    ## Project
    Name: [from registry]
    Docs path: [from registry]

    ## Manifest
    [full platform-docs.yaml content]

    ## Instructions
    Read the operations protocol at:
    .claude/protocols/platform-docs/references/operations-protocol.md

    Return a context package for the specified tier. This will be injected
    into downstream agent delegation prompts, so keep it concise and
    actionable — constraints and facts, not prose.
```

### Context Injection

The returned context is injected into the Delegation Prompt Template's Context section for all downstream agents in the pipeline:

```
Context:
  [existing file paths and prior agent output]
  
  Platform docs ([project name] — [repo key]):
    [context-read output verbatim]
```

Every agent in the pipeline sees this. No agent protocol changes needed.

---

## Step 3: Docs Deviation Report

### When It Runs

After the pipeline's final GATE passes and before returning to the user. Only runs if Step 1.5 ran (a documented repo was targeted).

### Operation: `deviation-check`

New operation type for the platform-docs agent:

```
Agent tool call:
  subagent_type: unicorn-team:platform-docs
  description: "deviation-check for [repo] — [project name]"
  prompt: |
    ## Operation
    Command: deviation-check
    Target repo: [repo key]

    ## What Was Just Implemented
    Summary: [pipeline summary — what changed]
    Files changed: [list from developer agent result]
    Tests: [count and coverage from pipeline]

    ## Docs Context Used (from Step 1.5)
    [the context-read output that was passed to agents]

    ## Project
    Name: [from registry]
    Docs path: [from registry]

    ## Manifest
    [full platform-docs.yaml]

    ## Instructions
    Compare what was implemented against the documentation.
    Return a deviation report with three sections:
    1. Checklist updates — items that should be marked complete
    2. Docs needing update — files where content is now stale
    3. No action needed — docs that are still accurate

    Be specific: file paths, line references, exact text to change.
    Do NOT make any changes — report only.
```

### Deviation Report Format

```markdown
## Docs Deviation Report ([project] — [repo])

### Checklist Updates
- `checklists/phase-4.md` line 23: `[ ] Result delivery Lambda` → mark `[x]`

### Docs Needing Update
- `reference/api-shapes.md`: Add 3 new endpoints (GET /api/users/me/runs, ...)
- `implementation/phases/phase-4-long-running-processes.md`: Update status 60% → 80%

### No Action Needed
- `architecture/overview.md`: Still accurate
- `decisions/ADR-0015`: Implementation matches decision
```

### User Approval Flow

The orchestrator appends the deviation report to its Response Format:

```markdown
## Summary
[existing]

## Quality Gates
[existing]

## Docs Deviation Report
[report from platform-docs agent]

**Apply these documentation updates?** (yes / no / selective)
```

Three responses:
- **yes** — orchestrator spawns platform-docs agent to make all listed changes, commits them in the docs repo
- **no** — skip; orchestrator returns as normal
- **selective** — user specifies which items to apply

---

## Extended `check-sync` Operation

The existing `check-sync` command gains a second dimension:

### Dimension 1: Internal Consistency (existing)

- Broken cross-references between documents
- ADR contradictions
- Stale technical constants (thresholds, protocols, namespaces)
- Phase plan dependency misalignment
- Terminology inconsistencies

### Dimension 2: Docs-vs-Code Drift (new)

For each repo in the manifest:
1. Read the repo's source code (key files, recent git log)
2. Compare against architecture docs, phase guides, and reference docs
3. Report:
   - **Implemented but undocumented** — code exists, docs don't reflect it
   - **Documented but not implemented** — docs say it exists, code doesn't
   - **Deviations from patterns** — code works differently than documented pattern
   - **Stale current-state reports** — last report older than 7 days

### Unified Report

```markdown
# Sync Check Report ([project name])

**Date**: YYYY-MM-DD
**Repos checked**: [list]

## Internal Consistency
[existing format]

## Docs-vs-Code Drift

### agentcore
- IMPLEMENTED NOT DOCUMENTED: [list]
- DOCUMENTED NOT IMPLEMENTED: [list]
- PATTERN DEVIATIONS: [list]
- REPORT STALENESS: Last report YYYYMMDD (N days ago)

### frontend-public
[same structure]

## Summary
| Dimension | Critical | Important | Minor |
|-----------|----------|-----------|-------|
| Internal consistency | N | N | N |
| Docs-vs-code drift | N | N | N |
```

---

## Files Changed

### Modified (unicorn-team)

| File | Change |
|------|--------|
| `skills/orchestrator/SKILL.md` | Add Step 1.5, Step 3, tier assignment table, context injection instructions |
| `.claude/protocols/platform-docs/references/operations-protocol.md` | Add `context-read` and `deviation-check` operations |
| `agents/platform-docs.md` | Add `context-read` and `deviation-check` to protocol overview |

### Not Changed

| File | Reason |
|------|--------|
| Agent definitions (developer, architect, etc.) | Context comes via delegation prompts, not protocol changes |
| `skills/platform-docs/SKILL.md` | Orchestrator calls agent directly; skill is for user-facing commands |
| `hooks/hooks.json` | SessionStart hook already provides ambient context |
| `platform-docs.yaml` (manifest) | No schema changes needed |
| Tests | No new files or structural changes; existing tests still pass |

---

## Edge Cases

**No active project:** Steps 1.5 and 3 are skipped. Pipelines work exactly as before.

**Target repo not in manifest:** Steps 1.5 and 3 are skipped for that repo. If PARALLEL pipeline has a mix of documented and undocumented repos, only documented ones get context.

**No current-state report exists:** Brief context notes "no prior report" and omits health status. Still provides constraints from architecture docs.

**Deviation check finds nothing:** Report says "No deviations found. Docs are current." No approval prompt shown.

**User declines deviation updates:** Orchestrator returns normally. Deviations remain unreported until next `check-sync` or next pipeline run against the same repo.

**context-read agent fails or times out:** Orchestrator logs warning, skips Step 1.5, proceeds with pipeline as if no docs project exists. Does not block implementation.

---

## Design Decisions

**Why inject context via prompt text, not file paths:** Agents get fresh 200K+ context windows. A 500-2000 token context summary is negligible. Passing file paths would require each agent to re-read the same docs, wasting their context on raw markdown instead of getting a curated summary.

**Why deviation-check is report-only:** Architecture docs are carefully maintained. Automated writes risk misinterpreting what changed (e.g., marking a phase complete when only one sub-item finished). User approval prevents doc corruption.

**Why brief/deep tiers instead of always-deep:** SIMPLE-FEATURE and BUG-FIX are fast paths. Adding 1500 tokens of architecture context to a 10-line bug fix adds latency and noise. Brief constraints ("don't use EDGE endpoints for SSE") are what these pipelines actually need.

**Why Step 1.5 spawns an agent instead of reading files directly:** The orchestrator runs in the main context. Reading 5-10 architecture docs would consume significant main-context tokens. The platform-docs agent does the reading in its own context and returns a concise summary.
