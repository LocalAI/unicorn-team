# Platform Docs Hardening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 17 issues found during double-check review — 4 high, 6 medium, 7 low severity — covering shell script safety, stale docs, missing manifest fields, skill gaps, and protocol clarity.

**Architecture:** All changes are to existing files in unicorn-team and lai-platform-docs. No new files. No structural changes. Tests should continue passing throughout (no count changes).

**Tech Stack:** Bash, Markdown, JSON, YAML, pytest

---

## File Structure

### Modified Files (unicorn-team)

| File | Issues Addressed |
|------|-----------------|
| `scripts/platform-context.sh` | #1 (quote injection), #17 (dead variable) |
| `CLAUDE.md` | #2 (stale "13 skills"), #7 (stale "200K") |
| `.claude/protocols/platform-docs/references/manifest-convention.md` | #3 (missing directories) |
| `skills/platform-docs/SKILL.md` | #4 (register validation), #6 (unregister), #11 (help text), #12 (overwrite protection), #15 (status format), #16 (drift trigger) |
| `.claude-plugin/plugin.json` | #5 (missing keywords) |
| `skills/orchestrator/SKILL.md` | #8 (routing ambiguity), #9 (repo detection), #10 (placeholder syntax) |
| `.claude/protocols/platform-docs/references/operations-protocol.md` | #10 (placeholder syntax) |

---

## Task 1: Fix shell script quote injection + remove dead variable

**Files:**
- Modify: `scripts/platform-context.sh:35-36` (remove dead REPO_COUNT)
- Modify: `scripts/platform-context.sh:65-75` (fix quote injection)

- [ ] **Step 1: Remove dead REPO_COUNT variable**

In `scripts/platform-context.sh`, find lines 35-36:

```bash
# Count repos in manifest (simple grep)
REPO_COUNT=$(grep -c '^\s\{2\}\w.*:$' "$DOCS_PATH/platform-docs.yaml" 2>/dev/null || echo "?")
```

Delete both lines entirely.

- [ ] **Step 2: Fix Python triple-quote injection**

Find lines 65-75:

```bash
python3 -c "
import json
ctx = '''$CTX'''
print(json.dumps({
    'continue': True,
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': ctx
    }
}, indent=2))
" 2>/dev/null || exit 0
```

Replace with:

```bash
CTX_JSON=$(CTX="$CTX" python3 -c "
import json, os
print(json.dumps({
    'continue': True,
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': os.environ['CTX']
    }
}, indent=2))
" 2>/dev/null) || exit 0
echo "$CTX_JSON"
```

This passes `$CTX` via environment variable instead of string interpolation, eliminating all injection risk.

- [ ] **Step 3: Verify the script runs correctly**

Run: `/Users/michaelhalagan/src/Libs/unicorn-team/scripts/platform-context.sh`

Expected: Valid JSON with `additionalContext` containing the project name

Run: `python3 -m json.tool <<< "$(/Users/michaelhalagan/src/Libs/unicorn-team/scripts/platform-context.sh)"`

Expected: Pretty-printed valid JSON

- [ ] **Step 4: Run tests**

Run: `pytest tests/test_scripts.py -v`

Expected: ALL PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/platform-context.sh
git commit -m "fix: use env var for JSON escaping, remove dead REPO_COUNT variable

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Fix stale CLAUDE.md references

**Files:**
- Modify: `CLAUDE.md:4,9,40,135`

- [ ] **Step 1: Update context window references**

In `CLAUDE.md`, find line 4:

```markdown
architecture where agents spawn as subprocesses with fresh 200K context windows.
```

Replace with:

```markdown
architecture where agents spawn as subprocesses with fresh context windows.
```

Find line 9:

```markdown
tool. Each gets a fresh 200K context window. Agent protocol content is inlined
```

Replace with:

```markdown
tool. Each gets a fresh context window. Agent protocol content is inlined
```

Find line 40:

```markdown
- Each agent gets fresh 200K context -- use it
```

Replace with:

```markdown
- Each agent gets a fresh context window -- use it
```

- [ ] **Step 2: Fix stale "13 skills" reference**

Find line 135:

```markdown
- `docs/skills.md` - All 13 skills, composition, and creation guide
```

Replace with:

```markdown
- `docs/skills.md` - All 15 skills, composition, and creation guide
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: fix stale context window and skill count references in CLAUDE.md

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Add missing directories to manifest convention

**Files:**
- Modify: `.claude/protocols/platform-docs/references/manifest-convention.md`

- [ ] **Step 1: Add checklists and patterns to Optional Fields**

Find the Optional Fields section (lines 39-56). After the `report_subdirs` block and before `## Defaults`, insert:

```markdown

# Additional directories used by some operations
# context-read (deep tier) reads patterns; deviation-check reads checklists
directories_optional:
  checklists: "checklists/"
  patterns: "implementation/patterns/"
```

- [ ] **Step 2: Document the optional directories**

After the line `All paths are relative to the docs repo root. Trailing slash optional.` (line 37), add:

```markdown

The following additional directories are optional. If present in the manifest,
the `context-read` (deep tier) and `deviation-check` operations will use them:

```yaml
directories:
  # ... required fields above ...
  checklists: "checklists/"          # Used by deviation-check for completable items
  patterns: "implementation/patterns/" # Used by context-read deep tier
```
```

- [ ] **Step 3: Update the example to include optional directories**

Find the example block (lines 80-100). In the `directories:` section, add after `architecture:`:

```yaml
  checklists: "checklists/"
  patterns: "implementation/patterns/"
```

- [ ] **Step 4: Commit**

```bash
git add .claude/protocols/platform-docs/references/manifest-convention.md
git commit -m "docs(platform-docs): add checklists and patterns to manifest convention

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Enhance platform-docs skill — register validation, unregister, help, overwrite protection, status format, drift trigger

**Files:**
- Modify: `skills/platform-docs/SKILL.md`

This task addresses issues #4, #6, #11, #12, #15, and #16 in one edit since they all touch the same file.

- [ ] **Step 1: Add "drift" to trigger phrases in description**

Find in the frontmatter (line 6):

```
  "check sync", "technical debt backlog",
```

Replace with:

```
  "check sync", "check drift", "docs drift", "technical debt backlog",
```

- [ ] **Step 2: Add `unregister` to command routing table**

Find the command routing table (lines 64-76). After the `register` row and before `status`, add:

```markdown
| `unregister <id>` | Direct | Remove a project from registry |
```

- [ ] **Step 3: Replace the `register` instructions with validation**

Find lines 100-108 (the `register` section). Replace:

```markdown
### `register <project-id> <path>`

1. Verify `<path>/platform-docs.yaml` exists
2. Read the manifest — extract `name` field
3. Read or create `~/.claude/platform-docs-registry.json`
4. Add entry: `"<project-id>": { "path": "<path>", "name": "<name>" }`
5. If no `active` project set, make this one active
6. Write the registry
7. Confirm: "Registered **{name}** as `<project-id>`"
```

Replace with:

```markdown
### `register <project-id> <path>`

1. Verify `<path>/platform-docs.yaml` exists — if not, error: "No manifest at {path}"
2. Read the manifest and validate:
   - `name` field present and non-empty
   - `id` field present and non-empty
   - `repos` has at least one entry with `path` and `dev_branch`
   - `directories` has at least `reports` and `architecture`
   - If validation fails, list which fields are missing
3. Read or create `~/.claude/platform-docs-registry.json`
4. If `<project-id>` already exists, warn: "Project `<id>` already registered. Overwrite? (yes/no)"
5. Add entry: `"<project-id>": { "path": "<path>", "name": "<name from manifest>" }`
6. If no `active` project set, make this one active
7. Write the registry
8. Confirm: "Registered **{name}** as `<project-id>`"

### `unregister <project-id>`

1. Read `~/.claude/platform-docs-registry.json`
2. Verify `<project-id>` exists in `projects` — if not, error: "Unknown project: {id}"
3. Remove the entry from `projects`
4. If this was the `active` project, clear `active` (set to empty string)
5. Write the registry
6. Confirm: "Removed **{name}**. Active project: {new active or 'none'}"
```

- [ ] **Step 4: Add help text for no-args invocation**

After the command routing table (after line 76), add:

```markdown

### (no arguments)

Display this help message:

```
Platform Docs — Documentation operations for registered projects.

Commands:
  list                          Show all registered projects
  switch <id>                   Change active project
  register <id> <path>          Add a new project (validates manifest)
  unregister <id>               Remove a project
  status                        Show active project health summary
  current-state [repo]          Full architecture audit (writes report)
  current-state-all             Parallel audit of all repos
  whats-next [repo]             Next work items and blockers
  check-phase [phase] [repo]    Phase readiness verification
  check-sync                    Docs consistency + docs-vs-code drift
  review-proposal [path]        Evaluate feature proposal

Active project: {name or "none — run 'register' first"}
```
```

- [ ] **Step 5: Add status output format**

Find the `status` section (lines 110-116). Replace:

```markdown
### `status`

1. Read active project's `platform-docs.yaml`
2. List all repos with labels
3. For each repo key, check `{directories.reports}/{repo}/` for latest report
4. Count items in `{directories.backlog}/`
5. Display summary table
```

Replace with:

```markdown
### `status`

1. Read active project's `platform-docs.yaml`
2. For each repo, find latest report in `{directories.reports}/{repo key}/`
3. Count DEBT items in `{directories.backlog}/`
4. Display:

```
LocalAI Platform (localai)
Docs: /path/to/lai-platform-docs

Repos:
  agentcore          Backend agent, CDK    Last report: 20260415-1200
  frontend-public    Public frontend       Last report: none
  frontend-platform  Platform frontend     Last report: 20260415-1200
  mcp-server         MCP server            Last report: none

Debt: 20 open items
```
```

- [ ] **Step 6: Verify skill is under 500 lines**

Run: `wc -l skills/platform-docs/SKILL.md`

Expected: Under 500 lines (was 152, adding ~50 lines → ~200)

- [ ] **Step 7: Run tests**

Run: `pytest tests/test_skills_valid.py -v`

Expected: ALL PASS

- [ ] **Step 8: Commit**

```bash
git add skills/platform-docs/SKILL.md
git commit -m "feat(platform-docs): add unregister, manifest validation, help text, overwrite protection

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Add missing keywords to plugin.json

**Files:**
- Modify: `.claude-plugin/plugin.json:11`

- [ ] **Step 1: Update keywords array**

Find line 11:

```json
  "keywords": ["orchestrator", "tdd", "code-review", "architecture", "devops", "security", "estimation", "polyglot"]
```

Replace with:

```json
  "keywords": ["orchestrator", "tdd", "code-review", "architecture", "devops", "security", "estimation", "polyglot", "platform-docs", "documentation"]
```

- [ ] **Step 2: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "chore: add platform-docs and documentation keywords to plugin.json

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Clarify orchestrator routing ambiguity and repo detection

**Files:**
- Modify: `skills/orchestrator/SKILL.md`

- [ ] **Step 1: Disambiguate classification tree**

Find line 49:

```
IF platform docs / architecture audit      → Invoke platform-docs skill. STOP.
```

Replace with:

```
IF platform docs query / docs audit / check-sync → Invoke platform-docs skill. STOP.
```

This removes "architecture audit" (which overlaps with ARCHITECTURE pipeline) and makes it specific to docs operations.

- [ ] **Step 2: Improve Step 1.5 repo detection guidance**

Find lines 68-74:

```
1. Check if SessionStart context mentions an active platform-docs project
   NO active project? → Skip Step 1.5.

2. Identify target repo from user's request:
   Working directory within a manifest repo path?
   User explicitly names a repo? File paths match a manifest repo?
   No match? → Skip Step 1.5.
```

Replace with:

```
1. Check SessionStart additionalContext for "Active platform-docs project:"
   NOT present? → Skip Step 1.5.
   Extract: project name, docs path from the context string.

2. Read the manifest at {docs_path}/platform-docs.yaml.
   Identify target repo by matching (first match wins):
   a. User's current working directory starts with a manifest repo path
   b. User's request explicitly names a repo key (e.g., "agentcore", "frontend")
   c. File paths in the request are under a manifest repo path
   No match? → Skip Step 1.5.
```

- [ ] **Step 3: Verify orchestrator is still under 500 lines**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ≤ 500

- [ ] **Step 4: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "fix(orchestrator): clarify docs routing and repo detection in Steps 1 and 1.5

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Fix placeholder syntax in operations protocol

**Files:**
- Modify: `.claude/protocols/platform-docs/references/operations-protocol.md`

- [ ] **Step 1: Replace curly-brace placeholders with square-bracket placeholders in context-read format**

Find lines 88-102 (the Format block in context-read):

```
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

Replace with:

```
**Format:**
```
Repo: [repo key] ([repo label])
Health: [summary from latest report or "No prior report"]
Phase: [phase name] — [completion %]
Constraints:
  - [constraint 1]
  - [constraint 2]
Debt: [N] items ([list if <= 3, else "see backlog/"])
[Deep tier only:]
Phase guide: [summary bullets]
Patterns: [applicable patterns]
ADRs: [relevant decisions]
Checklist: [applicable items]
```
```

NOTE: `{directories.reports}`, `{directories.phases}`, etc. in the procedure steps should KEEP curly braces — those reference manifest fields. Only the output format template placeholders change to square brackets.

- [ ] **Step 2: Commit**

```bash
git add .claude/protocols/platform-docs/references/operations-protocol.md
git commit -m "fix(platform-docs): use square-bracket placeholders in context-read output format

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Run full test suite and validate

**Files:** (none — verification only)

- [ ] **Step 1: Run all tests**

Run: `cd /Users/michaelhalagan/src/Libs/unicorn-team && pytest tests/ -v`

Expected: 123 tests, ALL PASS

- [ ] **Step 2: Run validate.sh**

Run: `./scripts/validate.sh`

Expected: All checks pass

- [ ] **Step 3: Verify orchestrator line count**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ≤ 500 lines

- [ ] **Step 4: Verify skill line count**

Run: `wc -l skills/platform-docs/SKILL.md`

Expected: ≤ 500 lines (should be ~200)

- [ ] **Step 5: Verify hook script outputs valid JSON**

Run: `scripts/platform-context.sh | python3 -m json.tool`

Expected: Valid JSON with `additionalContext` field

- [ ] **Step 6: Commit plan**

```bash
git add docs/superpowers/plans/2026-04-23-platform-docs-hardening.md
git commit -m "docs: add platform-docs hardening plan

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```
