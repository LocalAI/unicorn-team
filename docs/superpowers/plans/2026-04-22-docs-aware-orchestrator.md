# Docs-Aware Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the orchestrator automatically inject architecture docs context before every pipeline targeting a documented repo, and present a deviation report after implementation completes.

**Architecture:** Two new cross-cutting sections in the orchestrator (Step 1.5 and Step 3) wrap existing pipelines. Two new operations (`context-read` and `deviation-check`) are added to the platform-docs agent's operations protocol. The agent definition gets a brief update to mention the new operations. No pipeline internals, other agent definitions, or tests change.

**Tech Stack:** Markdown protocol documents (SKILL.md, operations-protocol.md, agent definition)

---

## File Structure

### Modified Files

| File | Lines Now | Change | Lines After (est.) |
|------|-----------|--------|-------------------|
| `.claude/protocols/platform-docs/references/operations-protocol.md` | 112 | Add `context-read` and `deviation-check` operations, extend `check-sync` | ~220 |
| `agents/platform-docs.md` | 94 | Add `context-read` and `deviation-check` to Context You Receive and Integration sections | ~110 |
| `skills/orchestrator/SKILL.md` | 400 | Add Step 1.5, Step 3, update Delegation Prompt Template and Response Format | ~490 |

### Not Changed

| File | Reason |
|------|--------|
| Other agent definitions | Context arrives via delegation prompts |
| `skills/platform-docs/SKILL.md` | Orchestrator calls agent directly |
| `hooks/hooks.json` | SessionStart hook already provides ambient context |
| Test files | No structural changes; existing tests still pass |

---

## Task 1: Add `context-read` operation to operations protocol

**Files:**
- Modify: `.claude/protocols/platform-docs/references/operations-protocol.md` (after line 58, before the `whats-next` operation)

- [ ] **Step 1: Read the current file**

Run: `cat -n .claude/protocols/platform-docs/references/operations-protocol.md`

Verify the file ends at line 112 and `## Operation: \`whats-next [repo]\`` is at line 60.

- [ ] **Step 2: Insert the `context-read` operation**

After the `current-state-all` operation block (after line 58) and before `## Operation: \`whats-next [repo]\`` (line 60), insert:

```markdown

## Operation: `context-read`

**Purpose:** Provide curated architecture context for downstream agents in orchestrator pipelines.

**Two tiers:**

### Brief (~500 tokens)

Return ONLY these four items as concise bullet points:
1. **Repo health** — from latest current-state report in `{directories.reports}/{repo}/`. If no report exists, say "No prior current-state report."
2. **Current phase** — read phase docs in `{directories.phases}`, identify which phase this repo is in and approximate completion.
3. **Critical constraints** — read the entry point doc (default: `CLAUDE.md`) for critical technical notes, gotchas, and warnings that affect this repo.
4. **Active debt** — count and list DEBT items in `{directories.backlog}` that mention this repo.

### Deep (~1500 tokens, includes all of Brief plus:)

5. **Phase guide summary** — read the current phase's implementation guide and summarize key requirements, acceptance criteria, and implementation patterns in 3-5 bullets.
6. **Applicable patterns** — read `{directories.patterns}` for patterns relevant to the task summary. Summarize each in one sentence.
7. **Relevant ADRs** — read `{directories.decisions}` for ADRs that affect this repo or the task area. List: ADR number, title, decision, key constraint.
8. **Compliance checklist** — extract checklist items from the current phase doc or checklists directory that apply to this repo.

**Input (from delegation prompt):**
- `Tier`: `brief` or `deep`
- `Target repo`: repo key from manifest
- `Task summary`: one-line description of what the user wants to do

**Output:** Plain text context package. No markdown headers — this will be injected verbatim into another agent's prompt. Use bullet points. Keep brief tier under 500 tokens and deep tier under 1500 tokens.

**Format:**
```
Repo: {repo key} ({repo label})
Health: {summary from latest report or "No prior report"}
Phase: {phase name} — {completion %}
Constraints:
  - {constraint 1}
  - {constraint 2}
Debt: {N} items ({list if <= 3, else "see backlog/"})
[Deep tier only:]
Phase guide: {summary bullets}
Patterns: {applicable patterns}
ADRs: {relevant decisions}
Checklist: {applicable items}
```

```

- [ ] **Step 3: Verify file is well-formed**

Run: `head -5 .claude/protocols/platform-docs/references/operations-protocol.md && echo "..." && wc -l .claude/protocols/platform-docs/references/operations-protocol.md`

Expected: Title line visible, line count increased by ~50 lines.

- [ ] **Step 4: Commit**

```bash
git add .claude/protocols/platform-docs/references/operations-protocol.md
git commit -m "feat(platform-docs): add context-read operation to protocol

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Add `deviation-check` operation to operations protocol

**Files:**
- Modify: `.claude/protocols/platform-docs/references/operations-protocol.md` (after the new `context-read` block, before `whats-next`)

- [ ] **Step 1: Insert the `deviation-check` operation**

After the `context-read` operation block and before `## Operation: \`whats-next [repo]\``, insert:

```markdown

## Operation: `deviation-check`

**Purpose:** Compare what was just implemented against documentation. Report-only — never write changes.

**Input (from delegation prompt):**
- `Target repo`: repo key from manifest
- `Summary`: what was implemented (from pipeline result)
- `Files changed`: list of modified/created files
- `Tests`: count and coverage from pipeline
- `Docs context used`: the context-read output that was passed to agents in Step 1.5

**Procedure:**
1. Read the docs context that was provided to agents (passed in the prompt)
2. Read the actual files that were changed in the source repo
3. Compare: do the changes align with documented architecture, patterns, and phase guides?
4. Check checklists in `{directories.checklists}` — are any items now completable?
5. Check phase docs in `{directories.phases}` — should completion % be updated?
6. Check reference docs (API shapes, event types, etc.) — do they need new entries?

**Output:** Deviation report with three sections:

```
## Docs Deviation Report ({project name} — {repo key})

### Checklist Updates
- `{file path}` line {N}: `[ ] {item}` — now complete, mark `[x]`
[or: "None — no checklist items affected."]

### Docs Needing Update
- `{file path}`: {what needs to change and why}
[or: "None — docs are current."]

### No Action Needed
- `{file path}`: Still accurate
```

If all three sections would say "None," return:
```
## Docs Deviation Report ({project name} — {repo key})

No deviations found. Documentation is current with this implementation.
```

**Important:** Do NOT make any changes to docs files. Report only. The orchestrator will ask the user for approval before applying updates.

```

- [ ] **Step 2: Verify line count**

Run: `wc -l .claude/protocols/platform-docs/references/operations-protocol.md`

Expected: ~210 lines (original 112 + ~50 context-read + ~50 deviation-check)

- [ ] **Step 3: Commit**

```bash
git add .claude/protocols/platform-docs/references/operations-protocol.md
git commit -m "feat(platform-docs): add deviation-check operation to protocol

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Extend `check-sync` with docs-vs-code drift

**Files:**
- Modify: `.claude/protocols/platform-docs/references/operations-protocol.md` (the existing `check-sync` operation, currently around line 83-92 in original, shifted by earlier insertions)

- [ ] **Step 1: Find and replace the `check-sync` operation**

Find the existing `check-sync` block. It currently reads:

```markdown
## Operation: `check-sync`

**Purpose:** Find internal inconsistencies in the docs repo.

**Procedure:**
1. Validate all cross-references between documents (broken links)
2. Check architecture docs vs implementation guides for contradictions
3. Check ADR consistency (superseded ADRs still referenced as current)
4. Check technical constants (thresholds, protocols, namespaces)
5. Return findings directly (do NOT write a report file)
```

Replace it with:

```markdown
## Operation: `check-sync`

**Purpose:** Find internal inconsistencies in the docs repo AND docs-vs-code drift across all repos in the manifest.

**Procedure:**

### Dimension 1: Internal Consistency

1. Validate all cross-references between documents (broken links)
2. Check architecture docs vs implementation guides for contradictions
3. Check ADR consistency (superseded ADRs still referenced as current)
4. Check technical constants (thresholds, protocols, namespaces)
5. Check terminology consistency across docs

### Dimension 2: Docs-vs-Code Drift

For each repo in the manifest:
1. Read the repo's key source files and recent git log (`git log --oneline -20`)
2. Compare against architecture docs, phase guides, and reference docs
3. Categorize findings:
   - **Implemented but undocumented** — code exists, docs don't reflect it
   - **Documented but not implemented** — docs say it exists, code doesn't
   - **Pattern deviations** — code works differently than documented pattern
   - **Stale reports** — latest current-state report older than 7 days

**Output:** Return findings directly (do NOT write a report file).

**Report format:**
```
# Sync Check Report ({project name})

**Date**: {YYYY-MM-DD}
**Repos checked**: {list from manifest}

## Internal Consistency

### Critical
- {issue with file paths}

### Important
- {issue}

### Minor
- {issue}

[or: "No internal consistency issues found."]

## Docs-vs-Code Drift

### {repo key}
- IMPLEMENTED NOT DOCUMENTED: {list or "None"}
- DOCUMENTED NOT IMPLEMENTED: {list or "None"}
- PATTERN DEVIATIONS: {list or "None"}
- REPORT STALENESS: Last report {date} ({N} days ago) [or "No reports"]

[repeat for each repo]

## Summary
| Dimension | Critical | Important | Minor |
|-----------|----------|-----------|-------|
| Internal consistency | {N} | {N} | {N} |
| Docs-vs-code drift | {N} | {N} | {N} |
```
```

- [ ] **Step 2: Verify file integrity**

Run: `grep -c "^## Operation:" .claude/protocols/platform-docs/references/operations-protocol.md`

Expected: 8 operations (current-state, current-state-all, context-read, deviation-check, whats-next, check-phase, check-sync, review-proposal)

- [ ] **Step 3: Commit**

```bash
git add .claude/protocols/platform-docs/references/operations-protocol.md
git commit -m "feat(platform-docs): extend check-sync with docs-vs-code drift dimension

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Update platform-docs agent definition

**Files:**
- Modify: `agents/platform-docs.md`

- [ ] **Step 1: Update "Context You Receive" section**

In `agents/platform-docs.md`, find lines 34-38:

```markdown
Your delegation prompt includes:
- **Project name** and **docs repo path**
- **Full manifest content** (repos, directories, report formats)
- **Operation** to execute (current-state, whats-next, check-phase, check-sync)
- **Target repo** (if applicable)
```

Replace with:

```markdown
Your delegation prompt includes:
- **Project name** and **docs repo path**
- **Full manifest content** (repos, directories, report formats)
- **Operation** to execute (current-state, whats-next, check-phase, check-sync, context-read, deviation-check)
- **Target repo** (if applicable)
- **Tier** (for context-read: brief or deep)
- **Implementation summary** (for deviation-check: what was built, files changed, tests)
```

- [ ] **Step 2: Update "Integration" section**

Find lines 89-94:

```markdown
## Integration

This agent is spawned by the `platform-docs` skill or the orchestrator's
`PLATFORM-DOCS` pipeline. The skill passes project context and manifest
content in the delegation prompt.

See: `.claude/protocols/platform-docs/references/manifest-convention.md`
```

Replace with:

```markdown
## Integration

This agent is spawned in three contexts:
1. **Platform-docs skill** — user invokes `/platform-docs [command]`; skill passes project context
2. **Orchestrator Step 1.5** — automatic `context-read` before pipelines targeting documented repos
3. **Orchestrator Step 3** — automatic `deviation-check` after pipeline completes on documented repos

For context-read: return concise text (no markdown headers) for injection into other agents' prompts.
For deviation-check: return a deviation report. Do NOT write changes — report only.

See: `.claude/protocols/platform-docs/references/manifest-convention.md`
See: `.claude/protocols/platform-docs/references/operations-protocol.md`
```

- [ ] **Step 3: Verify line count**

Run: `wc -l agents/platform-docs.md`

Expected: ~110 lines (original 94 + ~16 added)

- [ ] **Step 4: Run agent tests**

Run: `pytest tests/test_agents.py -v`

Expected: ALL PASS (34 tests — no structural changes, just body content edits)

- [ ] **Step 5: Commit**

```bash
git add agents/platform-docs.md
git commit -m "feat(platform-docs): add context-read and deviation-check to agent protocol

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Add Step 1.5 (Docs Context Enrichment) to orchestrator

**Files:**
- Modify: `skills/orchestrator/SKILL.md` (insert between Step 1 and Step 2, around line 59)

- [ ] **Step 1: Insert Step 1.5 after the classification block**

In `skills/orchestrator/SKILL.md`, find line 59:

```markdown
When in doubt, prefer the more structured pipeline.
```

After that line and before `## Step 2: Execute the Pipeline` (line 61), insert:

```markdown

## Step 1.5: Docs Context Enrichment

**Runs after classification, before pipeline execution. Skipped if no active
platform-docs project or if the target repo is not in the manifest.**

```
1. Check if SessionStart context mentions an active platform-docs project
   → NO active project? Skip Step 1.5 entirely.

2. Identify target repo from user's request:
   → Working directory within a manifest repo path?
   → User explicitly names a repo? ("implement X in agentcore")
   → File paths in request match a manifest repo path?
   → No match? Skip Step 1.5 entirely.

3. Determine context tier from the classified pipeline:
   → SIMPLE-FEATURE, BUG-FIX, DEPLOY, NEW-TECH → brief
   → COMPLEX-FEATURE, ARCHITECTURE, REVIEW       → deep
   → PARALLEL                                    → per-unit (each unit gets its own tier)

4. Spawn platform-docs agent for context-read:
   → subagent_type: unicorn-team:platform-docs
   → prompt:
     "## Operation
      Command: context-read
      Tier: [brief|deep]
      Target repo: [repo key]
      Task summary: [one-line summary of user's request]

      ## Project
      Name: [from SessionStart context]
      Docs path: [from SessionStart context]

      ## Manifest
      [Read the manifest at {docs_path}/platform-docs.yaml and include it here]

      ## Instructions
      Read the operations protocol at:
      .claude/protocols/platform-docs/references/operations-protocol.md
      Return a context package for the specified tier."

5. Store the returned context. It will be injected into the Context section
   of every downstream agent delegation prompt in Step 2.
```

If context-read fails or times out, log a warning and proceed without docs
context. Do not block the pipeline.

```

- [ ] **Step 2: Verify line count is under 500**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ~440 lines (original 400 + ~40 added). Must be ≤ 500.

- [ ] **Step 3: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "feat(orchestrator): add Step 1.5 docs context enrichment

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Update Delegation Prompt Template for context injection

**Files:**
- Modify: `skills/orchestrator/SKILL.md` (the Delegation Prompt Template section, around line 315 in original, shifted by Step 1.5 insertion)

- [ ] **Step 1: Find and replace the Delegation Prompt Template**

Find the current template:

```markdown
## Delegation Prompt Template

Every Agent tool call MUST include these four sections:

```
Task: [One clear objective. What to build/fix/review/design.]

Context: [File paths, design doc paths, prior agent output summaries.
  Keep under 2K tokens. Pass paths, not contents.]

Constraints: [TDD required, coverage threshold, technology choices,
  compatibility requirements, security requirements.]

Expected output: [Specific deliverables. File paths, test results,
  approval/rejection, coverage numbers.]
```
```

Replace with:

```markdown
## Delegation Prompt Template

Every Agent tool call MUST include these four sections:

```
Task: [One clear objective. What to build/fix/review/design.]

Context: [File paths, design doc paths, prior agent output summaries.
  Keep under 2K tokens. Pass paths, not contents.]

  IF Step 1.5 produced docs context, include it here:
  Platform docs ([project name] — [repo key]):
    [context-read output verbatim from Step 1.5]

Constraints: [TDD required, coverage threshold, technology choices,
  compatibility requirements, security requirements.]

Expected output: [Specific deliverables. File paths, test results,
  approval/rejection, coverage numbers.]
```
```

- [ ] **Step 2: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "feat(orchestrator): inject docs context into delegation prompt template

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Add Step 3 (Docs Deviation Report) to orchestrator

**Files:**
- Modify: `skills/orchestrator/SKILL.md` (insert after the Response Format section, before Error Recovery)

- [ ] **Step 1: Find the Response Format section end**

Find the end of the Response Format block. It ends with:

```markdown
## Notes
[Decisions made, tradeoffs taken, follow-up needed]
```
```

After the closing triple-backtick of the Response Format code block and before `## Error Recovery`, insert:

```markdown

## Step 3: Docs Deviation Report

**Runs after the final GATE passes, before returning to user. Skipped if
Step 1.5 did not run (no documented repo was targeted).**

```
1. Spawn platform-docs agent for deviation-check:
   → subagent_type: unicorn-team:platform-docs
   → prompt:
     "## Operation
      Command: deviation-check
      Target repo: [repo key from Step 1.5]

      ## What Was Just Implemented
      Summary: [pipeline summary from final GATE]
      Files changed: [list from agent results]
      Tests: [count and coverage]

      ## Docs Context Used
      [the context-read output from Step 1.5]

      ## Project
      Name: [project name]
      Docs path: [docs path]

      ## Manifest
      [full manifest content]

      ## Instructions
      Read the operations protocol at:
      .claude/protocols/platform-docs/references/operations-protocol.md
      Compare implementation against docs. Report deviations only — do NOT write changes."

2. IF the deviation report contains any Checklist Updates or Docs Needing Update:
   → Append the report to the Response Format output
   → Add: "**Apply these documentation updates?** (yes / no / selective)"
   → WAIT for user response
   → IF yes: spawn platform-docs agent to apply all listed changes, commit in docs repo
   → IF selective: user specifies which items; agent applies only those
   → IF no: proceed without changes

3. IF the deviation report says "No deviations found":
   → Append "Docs: Current (no updates needed)" to the Response Format Notes section
   → Do NOT prompt the user
```

If deviation-check fails or times out, skip Step 3 and return normally.
Note in the response: "Docs deviation check skipped (agent unavailable)."

```

- [ ] **Step 2: Update the Response Format to include deviation report slot**

Find the Response Format section. After the `## Notes` line inside the code block, add:

```markdown

## Docs Deviation Report
[If Step 3 ran and found deviations — included automatically]
[If no deviations: "Docs: Current (no updates needed)"]
```

- [ ] **Step 3: Verify line count is under 500**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ~490 lines. MUST be ≤ 500. If over, check for unnecessary blank lines to trim.

- [ ] **Step 4: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "feat(orchestrator): add Step 3 docs deviation report with user approval

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Add Platform-Docs agent to orchestrator Agent Registry

**Files:**
- Modify: `skills/orchestrator/SKILL.md` (the Agent Registry table, around line 33)

- [ ] **Step 1: Add platform-docs to the registry table**

Find the Agent Registry table:

```markdown
| Agent | subagent_type | Model | Use For |
|-------|--------------|-------|---------|
| Developer | `unicorn-team:developer` | sonnet | Code, tests, bug fixes, refactoring |
| Architect | `unicorn-team:architect` | opus | ADRs, API contracts, system design |
| QA | `unicorn-team:qa-security` | sonnet | Code review, security audit, quality gates |
| DevOps | `unicorn-team:devops` | sonnet | CI/CD, IaC, deployment, monitoring |
| Polyglot | `unicorn-team:polyglot` | opus | New languages, cross-ecosystem patterns |
```

Add one row after Polyglot:

```markdown
| Platform-Docs | `unicorn-team:platform-docs` | opus | Docs context, deviation checks, current-state audits |
```

- [ ] **Step 2: Verify line count still under 500**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ~491 lines. Must be ≤ 500.

- [ ] **Step 3: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "feat(orchestrator): add platform-docs agent to registry table

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Run full test suite and validate

**Files:** (none — verification only)

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v`

Expected: 123 tests, ALL PASS. No structural changes were made (no new files, no renamed files, no count changes), so all existing tests should still pass.

- [ ] **Step 2: Run validate.sh**

Run: `./scripts/validate.sh`

Expected: All 7 checks pass. Skills count still 15, agents still 6.

- [ ] **Step 3: Verify orchestrator line count**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ≤ 500 lines. If over 500, the orchestrator skill will fail the `test_skill_under_500_lines` test. If this happens, identify blank lines or verbose sections to trim.

- [ ] **Step 4: Verify operations protocol has all 8 operations**

Run: `grep "^## Operation:" .claude/protocols/platform-docs/references/operations-protocol.md`

Expected:
```
## Operation: `current-state [repo]`
## Operation: `current-state-all`
## Operation: `context-read`
## Operation: `deviation-check`
## Operation: `whats-next [repo]`
## Operation: `check-phase [phase] [repo]`
## Operation: `check-sync`
## Operation: `review-proposal [path]`
```

- [ ] **Step 5: Verify agent mentions new operations**

Run: `grep -c "context-read\|deviation-check" agents/platform-docs.md`

Expected: At least 4 matches (mentioned in Context You Receive and Integration sections)

- [ ] **Step 6: Commit plan as done**

```bash
git add docs/superpowers/plans/2026-04-22-docs-aware-orchestrator.md
git commit -m "docs: add docs-aware orchestrator implementation plan

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```
