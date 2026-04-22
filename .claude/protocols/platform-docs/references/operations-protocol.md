# Platform Docs Operations Protocol

Detailed procedures for each operation the platform-docs agent performs.
The agent reads the project manifest at runtime for repo paths and directory conventions.

## Operation: `current-state [repo]`

**Purpose:** Full architecture compliance audit of a source repo against docs.

**Procedure:**
1. Read manifest to resolve `[repo]` to a filesystem path
2. Read the docs repo's entry point (default: `CLAUDE.md`)
3. Read relevant architecture docs from `directories.architecture`
4. Explore the source repo -- prioritize actual source code over documentation
5. Compare implementation against architecture for each compliance item
6. Generate report with ✅/⚠️/❌ status per item, citing `file:line`

**Output:** Write to `{directories.reports}/{repo}/CURRENT_STATE-{YYYYMMDD-HHMM}.md`

**Report template:**
```
# {Repo Label} Current State Report

> **Generated**: {YYYY-MM-DD HH:MM}
> **Repository**: {repo key}
> **Project**: {project name}

## Executive Summary
[3-5 sentences: health, compliance %, critical issues]

## Architecture Compliance
- ✅ [Item]: [evidence with file:line]
- ⚠️ [Item]: [partial -- what's done, what's missing]
- ❌ [Item]: [not found, expected at path]

## Technical Debt Discovered
| Item | Description | Severity |
|------|-------------|----------|

## Recommendations
1. [Prioritized, actionable]

## Files Analyzed
- `path/to/file.py` -- [what was checked]
```

## Operation: `current-state-all`

**Purpose:** Parallel audit of all repos + synthesized rollup.

**Procedure:**
1. Read manifest to get all repos
2. Spawn one parallel Agent per repo (subagent_type: Explore)
3. Each agent runs the `current-state` procedure for its repo
4. Write individual reports
5. Synthesize a platform rollup report comparing all repos

**Output:** One report per repo + `{directories.reports}/platform/CURRENT_STATE-{YYYYMMDD-HHMM}.md`

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
6. **Applicable patterns** — read files in the patterns directory for patterns relevant to the task summary. Summarize each in one sentence.
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

## Operation: `whats-next [repo]`

**Purpose:** Determine next work items, blockers, and priorities.

**Procedure:**
1. Read phase documents from `directories.phases`
2. Read latest current-state report for `[repo]`
3. Read the source repo's recent git log (`git log --oneline -20`)
4. Identify: completed phases, current phase progress, blockers
5. Return analysis directly (do NOT write a report file)

**Output:** Direct response with prioritized next steps.

## Operation: `check-phase [phase] [repo]`

**Purpose:** Verify specific phase readiness for a repo.

**Procedure:**
1. Read the phase document from `directories.phases`
2. Explore the source repo for implementation evidence
3. Generate checklist with pass/fail per requirement
4. Write report to `{directories.reports}/{repo}/PHASE_CHECK-{YYYYMMDD-HHMM}.md`

## Operation: `check-sync`

**Purpose:** Find internal inconsistencies in the docs repo.

**Procedure:**
1. Validate all cross-references between documents (broken links)
2. Check architecture docs vs implementation guides for contradictions
3. Check ADR consistency (superseded ADRs still referenced as current)
4. Check technical constants (thresholds, protocols, namespaces)
5. Return findings directly (do NOT write a report file)

## Operation: `review-proposal [path]`

**Purpose:** Review a feature proposal against architecture.

**Procedure:**
1. Read the proposal document
2. Read relevant architecture docs and ADRs
3. Evaluate: vision alignment, technical feasibility, architectural fit
4. Return structured review with approve/concerns/reject recommendation

## Quality Gate (All Operations)

Before returning any result:
- [ ] All file references are to files that actually exist
- [ ] Status indicators (✅/⚠️/❌) match observed evidence
- [ ] Recommendations are specific and actionable (file paths, not vague)
- [ ] No placeholder text (TBD, TODO, etc.)
- [ ] Report uses the project's report format conventions
