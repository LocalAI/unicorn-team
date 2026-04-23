# Platform Docs Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a multi-project documentation operations system to the unicorn-team plugin — a dedicated agent and skill that can audit, check, and report on any documentation repository that follows a standardized manifest convention.

**Architecture:** A user-local registry (`~/.claude/platform-docs-registry.json`) maps project IDs to docs repo paths. Each docs repo provides a `platform-docs.yaml` manifest declaring its repos, directories, and report formats. A new `platform-docs` skill handles project switching and lightweight lookups via shell injection. A new `platform-docs` agent (Opus, 200K context) handles heavy operations (current-state audits, phase checks, sync verification). A SessionStart hook injects active project context into every conversation.

**Tech Stack:** YAML manifest, JSON registry, Bash hook script, Markdown agent/skill definitions, pytest validation

---

## File Structure

### New Files (unicorn-team)

| File | Responsibility |
|------|---------------|
| `agents/platform-docs.md` | Agent definition — generic docs operations protocol (~130 lines) |
| `skills/platform-docs/SKILL.md` | User-facing skill — project switching, context injection, delegation (~180 lines) |
| `.claude/protocols/platform-docs/references/manifest-convention.md` | Defines what `platform-docs.yaml` must contain |
| `.claude/protocols/platform-docs/references/operations-protocol.md` | Detailed procedures for each operation type |
| `scripts/platform-context.sh` | SessionStart hook — injects active project summary |

### Modified Files (unicorn-team)

| File | Change |
|------|--------|
| `tests/test_agents.py:25,74` | `EXPECTED_AGENTS` add `"platform-docs"`, count 5→6 |
| `tests/test_plugin.py:88` | Skill count 14→15 |
| `tests/test_hooks.py:21-26` | Add `"SessionStart"` to `VALID_HOOK_EVENTS` |
| `hooks/hooks.json` | Add `SessionStart` hook entry |
| `skills/orchestrator/SKILL.md:45-56` | Add `PLATFORM-DOCS` pipeline route |
| `CLAUDE.md:20-27` | Add agent to table, update description |
| `.claude-plugin/plugin.json` | Bump version to 2.3.0, update description |
| `scripts/validate.sh:34,36` | Fix skill count 13→15 |

### New Files (lai-platform-docs)

| File | Responsibility |
|------|---------------|
| `platform-docs.yaml` | Project manifest — repos, directories, report formats |

### Modified Files (lai-platform-docs)

| File | Change |
|------|--------|
| `.claude/skills/platform-architecture/` | Delete (subsumed by agent) |
| `.claude/skills/streaming-patterns/` | Delete (subsumed by agent) |
| `.claude/skills/dual-mode-auth/` | Delete (subsumed by agent) |
| `.claude/skills/mvp-plan-sync/` | Delete (subsumed by agent) |
| `.claude/skills/docs-sync-review/SKILL.md` | Refresh with current repo mapping |
| `CLAUDE.md:302-310` | Update Skills section to reflect removals |

### New Files (user-local)

| File | Responsibility |
|------|---------------|
| `~/.claude/platform-docs-registry.json` | Maps project IDs to docs repo paths |

---

## Phase 1: RED — Update Tests

### Task 1: Update test expectations for 6 agents

**Files:**
- Modify: `tests/test_agents.py:25` (EXPECTED_AGENTS set)
- Modify: `tests/test_agents.py:74` (count assertion)

- [ ] **Step 1: Edit EXPECTED_AGENTS set**

In `tests/test_agents.py`, change line 25 from:

```python
EXPECTED_AGENTS = {"developer", "architect", "qa-security", "devops", "polyglot"}
```

to:

```python
EXPECTED_AGENTS = {"developer", "architect", "qa-security", "devops", "polyglot", "platform-docs"}
```

- [ ] **Step 2: Edit count assertion**

In `tests/test_agents.py`, change line 74 from:

```python
    assert len(agent_files) == 5, (
        f"Expected 5 agent definitions in agents/, "
```

to:

```python
    assert len(agent_files) == 6, (
        f"Expected 6 agent definitions in agents/, "
```

- [ ] **Step 3: Run agent tests to verify RED**

Run: `cd /Users/michaelhalagan/src/Libs/unicorn-team && pytest tests/test_agents.py -v`

Expected: FAIL — `Expected 6 agent definitions in agents/, found 5` and agent names mismatch with `Missing: {'platform-docs'}`

- [ ] **Step 4: Commit**

```bash
git add tests/test_agents.py
git commit -m "test: expect 6 agents including platform-docs"
```

### Task 2: Update test expectations for 15 skills

**Files:**
- Modify: `tests/test_plugin.py:88-89`

- [ ] **Step 1: Edit skill count assertion**

In `tests/test_plugin.py`, change lines 88-89 from:

```python
    assert len(skill_files) == 14, (
        f"Expected 14 skills at skills/*/SKILL.md, found {len(skill_files)}: "
```

to:

```python
    assert len(skill_files) == 15, (
        f"Expected 15 skills at skills/*/SKILL.md, found {len(skill_files)}: "
```

- [ ] **Step 2: Run plugin tests to verify RED**

Run: `pytest tests/test_plugin.py::test_all_14_skills_discoverable -v`

Expected: FAIL — `Expected 15 skills at skills/*/SKILL.md, found 14`

- [ ] **Step 3: Commit**

```bash
git add tests/test_plugin.py
git commit -m "test: expect 15 skills including platform-docs"
```

### Task 3: Update test expectations for SessionStart hook event

**Files:**
- Modify: `tests/test_hooks.py:21-26`

- [ ] **Step 1: Add SessionStart to VALID_HOOK_EVENTS**

In `tests/test_hooks.py`, change lines 21-26 from:

```python
VALID_HOOK_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "Stop",
}
```

to:

```python
VALID_HOOK_EVENTS = {
    "SessionStart",
    "PreToolUse",
    "PostToolUse",
    "Notification",
    "Stop",
}
```

- [ ] **Step 2: Run hook tests to verify still GREEN** (no SessionStart in hooks.json yet)

Run: `pytest tests/test_hooks.py -v`

Expected: PASS (adding to the valid set doesn't break anything; we haven't added the hook yet)

- [ ] **Step 3: Commit**

```bash
git add tests/test_hooks.py
git commit -m "test: add SessionStart to valid hook events"
```

---

## Phase 2: GREEN — Create Agent + Protocols

### Task 4: Create protocol reference directories and manifest convention

**Files:**
- Create: `.claude/protocols/platform-docs/references/manifest-convention.md`

- [ ] **Step 1: Create directory structure**

Run: `mkdir -p /Users/michaelhalagan/src/Libs/unicorn-team/.claude/protocols/platform-docs/references`

- [ ] **Step 2: Write manifest-convention.md**

Create `.claude/protocols/platform-docs/references/manifest-convention.md`:

```markdown
# Platform Docs Manifest Convention

Every documentation repository that works with the `platform-docs` agent must
include a `platform-docs.yaml` file at its root.

## Required Fields

```yaml
# Human-readable project name
name: "My Platform"

# Short identifier (matches registry key)
id: "my-platform"

# Source code repositories this docs repo covers
repos:
  <repo-key>:                    # Short identifier used in commands
    path: "/absolute/path/to/repo"
    dev_branch: "main"           # Branch PRs target
    label: "Human-readable role"
```

At least one repo must be defined.

## Required Directories

```yaml
# Where docs are organized (relative to docs repo root)
directories:
  reports: "current-state/"      # Timestamped report output
  phases: "implementation/phases/"
  decisions: "decisions/"
  backlog: "backlog/"
  architecture: "architecture/"
```

All paths are relative to the docs repo root. Trailing slash optional.

## Optional Fields

```yaml
# Report filename conventions
report_formats:
  current_state: "CURRENT_STATE-{YYYYMMDD-HHMM}.md"
  phase_check: "PHASE_CHECK-{YYYYMMDD-HHMM}.md"
  sync_check: "SYNC_CHECK-{YYYYMMDD-HHMM}.md"

# Entry point document (defaults to CLAUDE.md)
entry_point: "CLAUDE.md"

# Per-repo report subdirectories inside reports dir
# Defaults to repo key name
report_subdirs:
  agentcore: "agentcore/"
  frontend: "frontend-public/"
```

## Defaults

If `report_formats` is omitted, the agent uses:
- `CURRENT_STATE-{YYYYMMDD-HHMM}.md`
- `PHASE_CHECK-{YYYYMMDD-HHMM}.md`
- `SYNC_CHECK-{YYYYMMDD-HHMM}.md`

If `entry_point` is omitted, the agent reads `CLAUDE.md`.

If `report_subdirs` is omitted, the agent uses repo keys as subdirectory names.

## Validation

The `platform-docs` skill validates on `register`:
1. File exists at `<path>/platform-docs.yaml`
2. `name` field is present and non-empty
3. `id` field is present and non-empty
4. `repos` has at least one entry with `path` and `dev_branch`
5. `directories` has at least `reports` and `architecture`

## Example

```yaml
name: "LocalAI Platform"
id: "localai"

repos:
  agentcore:
    path: "/Users/me/src/Agents/lai-aws-bedrock-agentcore-python"
    dev_branch: "main"
    label: "Backend agent, CDK, gateway, Cedar"
  frontend-public:
    path: "/Users/me/src/UI/lai-localai-home"
    dev_branch: "development"
    label: "Public frontend"

directories:
  reports: "current-state/"
  phases: "implementation/phases/"
  decisions: "decisions/"
  backlog: "backlog/"
  architecture: "architecture/"
```
```

- [ ] **Step 3: Commit**

```bash
git add .claude/protocols/platform-docs/references/manifest-convention.md
git commit -m "feat(platform-docs): add manifest convention reference"
```

### Task 5: Create operations protocol reference

**Files:**
- Create: `.claude/protocols/platform-docs/references/operations-protocol.md`

- [ ] **Step 1: Write operations-protocol.md**

Create `.claude/protocols/platform-docs/references/operations-protocol.md`:

```markdown
# Platform Docs Operations Protocol

Detailed procedures for each operation the platform-docs agent performs.
The agent reads the project manifest at runtime for repo paths and directory conventions.

## Operation: `current-state [repo]`

**Purpose:** Full architecture compliance audit of a source repo against docs.

**Procedure:**
1. Read manifest to resolve `[repo]` to a filesystem path
2. Read the docs repo's entry point (default: `CLAUDE.md`)
3. Read relevant architecture docs from `directories.architecture`
4. Explore the source repo — prioritize actual source code over documentation
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
- ⚠️ [Item]: [partial — what's done, what's missing]
- ❌ [Item]: [not found, expected at path]

## Technical Debt Discovered
| Item | Description | Severity |
|------|-------------|----------|

## Recommendations
1. [Prioritized, actionable]

## Files Analyzed
- `path/to/file.py` — [what was checked]
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
```

- [ ] **Step 2: Commit**

```bash
git add .claude/protocols/platform-docs/references/operations-protocol.md
git commit -m "feat(platform-docs): add operations protocol reference"
```

### Task 6: Create platform-docs agent definition

**Files:**
- Create: `agents/platform-docs.md`

- [ ] **Step 1: Write the agent definition**

Create `agents/platform-docs.md`:

```markdown
---
name: platform-docs
description: >-
  Platform documentation operations agent. Reads architecture docs, ADRs,
  implementation guides, and source repos. Generates current-state reports,
  phase checks, gap analyses, sync verification, and whats-next analysis.
  Works with any docs repo that follows the platform-docs manifest convention.
model: opus
tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
skills:
  - self-verification
  - code-reading
  - technical-debt
---

# Platform Docs Agent — Execution Protocol

You are a documentation operations specialist. You read architecture docs and
source code, then generate structured reports. You work with any documentation
repository that provides a `platform-docs.yaml` manifest.

## Prime Directive

**Read actual files. Never assume content. Always verify against current state.**

## Context You Receive

Your delegation prompt includes:
- **Project name** and **docs repo path**
- **Full manifest content** (repos, directories, report formats)
- **Operation** to execute (current-state, whats-next, check-phase, check-sync)
- **Target repo** (if applicable)

## Step 1: Load Project Context

1. Parse the manifest from your delegation prompt
2. Read the docs repo's entry point (`CLAUDE.md` unless manifest overrides)
3. If targeting a specific repo, read its implementation guide from the docs

## Step 2: Execute Operation

Read the operations protocol for detailed procedures:

See: `.claude/protocols/platform-docs/references/operations-protocol.md`

Match your operation to the protocol and follow it exactly.

## Step 3: Write Output

For operations that produce report files:
1. Use the manifest's `directories.reports` path
2. Use the manifest's `report_formats` naming convention (or defaults)
3. Use the current timestamp: `{YYYYMMDD-HHMM}` in local time
4. Create subdirectories if they don't exist (`mkdir -p`)

For operations that return directly (whats-next, check-sync):
1. Return structured findings in your response
2. Do NOT create report files

## Step 4: Quality Gate

Before returning:
- [ ] Every file path I cited actually exists (verified with Read or Bash)
- [ ] Status indicators match evidence I found
- [ ] Recommendations include specific file paths and actions
- [ ] No placeholder or assumed content

## Return Format

```yaml
summary: "Generated [report type] for [repo] in [project name]"
files_written:
  - "path/to/report.md"
findings:
  critical: 0
  important: 0
  minor: 0
key_recommendations:
  - "recommendation with file path"
```

## Integration

This agent is spawned by the `platform-docs` skill or the orchestrator's
`PLATFORM-DOCS` pipeline. The skill passes project context and manifest
content in the delegation prompt.

See: `.claude/protocols/platform-docs/references/manifest-convention.md`
```

- [ ] **Step 2: Run agent tests to verify GREEN**

Run: `pytest tests/test_agents.py -v`

Expected: PASS — 6 agents found, names match, frontmatter valid, skills resolve

- [ ] **Step 3: Commit**

```bash
git add agents/platform-docs.md
git commit -m "feat(platform-docs): add documentation operations agent"
```

---

## Phase 3: GREEN — Create Skill

### Task 7: Create platform-docs skill

**Files:**
- Create: `skills/platform-docs/SKILL.md`

- [ ] **Step 1: Create skill directory**

Run: `mkdir -p /Users/michaelhalagan/src/Libs/unicorn-team/skills/platform-docs`

- [ ] **Step 2: Write SKILL.md**

Create `skills/platform-docs/SKILL.md`:

```markdown
---
name: platform-docs
description: >-
  Platform documentation operations across multiple projects. ALWAYS trigger on
  "platform docs", "current state", "whats next", "check phase", "ADR",
  "architecture review", "platform status", "check sync", "technical debt backlog",
  "mvp sync", "phase progress", "streaming pattern", "dual mode auth",
  "platform architecture", "switch project", "register project", "docs manifest".
  Use when querying platform architecture, checking implementation status, auditing
  repos against documentation, or managing documentation projects.
  Different from orchestrator which handles code implementation.
argument-hint: "[command] [args...]"
allowed-tools: "Read Write Edit Grep Glob Bash(find *) Bash(git *) Bash(python3 *) Bash(cat *) Bash(ls *) Bash(mkdir *) Bash(wc *)"
---

# Platform Docs Operations

Manage and query documentation repositories that follow the platform-docs
manifest convention. Supports multiple isolated projects with switching.

## Active Project

!`python3 -c "
import json, os, sys
reg = os.path.expanduser('~/.claude/platform-docs-registry.json')
if not os.path.exists(reg):
    print('**No registry.** Run: /unicorn-team:platform-docs register <id> <path>')
    sys.exit(0)
r = json.load(open(reg))
active = r.get('active', '')
if not active:
    print('**No active project.** Run: /unicorn-team:platform-docs switch <id>')
    sys.exit(0)
p = r.get('projects', {}).get(active, {})
name = p.get('name', active)
path = p.get('path', 'unknown')
exists = 'exists' if os.path.isdir(path) else 'NOT FOUND'
print(f'**{name}** (\`{active}\`) at \`{path}\` ({exists})')
" 2>/dev/null || echo "Registry not readable."`

## Project Manifest

!`python3 -c "
import json, os, sys
reg = os.path.expanduser('~/.claude/platform-docs-registry.json')
if not os.path.exists(reg):
    sys.exit(0)
r = json.load(open(reg))
active = r.get('active', '')
path = r.get('projects', {}).get(active, {}).get('path', '')
manifest = os.path.join(path, 'platform-docs.yaml')
if os.path.exists(manifest):
    print(open(manifest).read())
else:
    print(f'No platform-docs.yaml found at {path}')
" 2>/dev/null`

---

## Command Routing

Parse `$ARGUMENTS` and route to the appropriate handler:

| Command | Handler | Description |
|---------|---------|-------------|
| `list` | Direct | Show all registered projects |
| `switch <id>` | Direct | Change active project |
| `register <id> <path>` | Direct | Add a new project |
| `status` | Direct | Show active project health summary |
| `current-state [repo]` | Agent | Full architecture audit |
| `current-state-all` | Agent | Parallel audit of all repos |
| `whats-next [repo]` | Agent | Next work items and blockers |
| `check-phase [phase] [repo]` | Agent | Phase readiness verification |
| `check-sync` | Agent | Internal docs consistency check |
| `review-proposal [path]` | Agent | Evaluate feature proposal |
| (no args / help) | Direct | Show this command list |

## Direct Operations

### `list`

Read `~/.claude/platform-docs-registry.json` and display all projects:

```
Projects:
  ► localai  — LocalAI Platform (/path/to/lai-platform-docs)
    client-x — Client X (/path/to/client-x-docs)
```

Mark active project with `►`.

### `switch <project-id>`

1. Read `~/.claude/platform-docs-registry.json`
2. Verify `<project-id>` exists in `projects`
3. Update `active` to `<project-id>`
4. Write the updated registry back
5. Confirm: "Switched active project to **{name}**"

### `register <project-id> <path>`

1. Verify `<path>/platform-docs.yaml` exists
2. Read the manifest — extract `name` field
3. Read or create `~/.claude/platform-docs-registry.json`
4. Add entry: `"<project-id>": { "path": "<path>", "name": "<name>" }`
5. If no `active` project set, make this one active
6. Write the registry
7. Confirm: "Registered **{name}** as `<project-id>`"

### `status`

1. Read active project's `platform-docs.yaml`
2. List all repos with labels
3. For each repo key, check `{directories.reports}/{repo}/` for latest report
4. Count items in `{directories.backlog}/`
5. Display summary table

## Agent Operations

For `current-state`, `whats-next`, `check-phase`, `check-sync`, and
`review-proposal`, delegate to the platform-docs agent.

**Delegation template:**

```
Agent tool call:
  subagent_type: unicorn-team:platform-docs
  description: "[command] [repo] — [project name]"
  prompt: |
    ## Project
    Name: {name}
    Docs path: {path from registry}

    ## Manifest
    {full platform-docs.yaml content}

    ## Operation
    Command: {command}
    Target: {repo or "all"}

    ## Instructions
    Read the operations protocol at:
    .claude/protocols/platform-docs/references/operations-protocol.md

    Execute the operation. Write reports to the manifest's configured
    reports directory. Return the standard platform-docs result format.
```

Read the manifest content from the active project's `platform-docs.yaml`
and include it verbatim in the delegation prompt so the agent has all
repo paths, directory conventions, and report formats without needing
to resolve the registry itself.
```

- [ ] **Step 3: Run skill tests to verify GREEN**

Run: `pytest tests/test_plugin.py tests/test_skills_valid.py -v`

Expected: PASS — 15 skills found, frontmatter valid, description has triggers, body under 500 lines

- [ ] **Step 4: Commit**

```bash
git add skills/platform-docs/SKILL.md
git commit -m "feat(platform-docs): add user-facing documentation operations skill"
```

---

## Phase 4: GREEN — Create Hook

### Task 8: Create SessionStart hook script

**Files:**
- Create: `scripts/platform-context.sh`

- [ ] **Step 1: Write the hook script**

Create `scripts/platform-context.sh`:

```bash
#!/usr/bin/env bash
# platform-context.sh — SessionStart hook that injects active platform-docs
# project context into every conversation.
#
# Output: JSON with additionalContext field for Claude Code SessionStart hook.
# Exits silently (exit 0) if no registry or active project is configured.

REGISTRY="$HOME/.claude/platform-docs-registry.json"

if [ ! -f "$REGISTRY" ]; then
    exit 0
fi

# Read active project path and name from registry (stdlib json only)
read -r ACTIVE DOCS_PATH PROJECT_NAME <<< "$(python3 -c "
import json, sys
try:
    r = json.load(open('$REGISTRY'))
    a = r.get('active', '')
    p = r.get('projects', {}).get(a, {})
    print(a, p.get('path', ''), p.get('name', a))
except Exception:
    print('', '', '')
" 2>/dev/null)"

if [ -z "$DOCS_PATH" ] || [ ! -d "$DOCS_PATH" ]; then
    exit 0
fi

# Verify manifest exists
if [ ! -f "$DOCS_PATH/platform-docs.yaml" ]; then
    exit 0
fi

# Count repos in manifest (simple grep)
REPO_COUNT=$(grep -c '^\s\{2\}\w.*:$' "$DOCS_PATH/platform-docs.yaml" 2>/dev/null || echo "?")

# Find latest platform rollup report
REPORTS_DIR="$DOCS_PATH/current-state/platform"
LATEST_REPORT=""
if [ -d "$REPORTS_DIR" ]; then
    LATEST_REPORT=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -1)
fi
REPORT_DATE=""
if [ -n "$LATEST_REPORT" ]; then
    REPORT_DATE=$(basename "$LATEST_REPORT" | grep -o '[0-9]\{8\}-[0-9]\{4\}' | head -1)
fi

# Count open debt items
BACKLOG_DIR="$DOCS_PATH/backlog"
DEBT_COUNT=0
if [ -d "$BACKLOG_DIR" ]; then
    DEBT_COUNT=$(find "$BACKLOG_DIR" -name "DEBT-*.md" -not -name "TEMPLATE*" -not -name "README*" 2>/dev/null | wc -l | tr -d ' ')
fi

# Build context string
CTX="Active platform-docs project: $PROJECT_NAME ($ACTIVE). Docs: $DOCS_PATH."
if [ -n "$REPORT_DATE" ]; then
    CTX="$CTX Latest rollup: $REPORT_DATE."
fi
if [ "$DEBT_COUNT" -gt 0 ]; then
    CTX="$CTX Open debt: $DEBT_COUNT items."
fi

# Escape for JSON
CTX_ESCAPED=$(echo "$CTX" | sed 's/\\/\\\\/g; s/"/\\"/g')

cat <<EOF
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "$CTX_ESCAPED"
  }
}
EOF
```

- [ ] **Step 2: Make script executable**

Run: `chmod +x /Users/michaelhalagan/src/Libs/unicorn-team/scripts/platform-context.sh`

- [ ] **Step 3: Verify shebang and permissions**

Run: `head -1 scripts/platform-context.sh && ls -la scripts/platform-context.sh`

Expected: `#!/usr/bin/env bash` and `-rwxr-xr-x`

- [ ] **Step 4: Commit**

```bash
git add scripts/platform-context.sh
git commit -m "feat(platform-docs): add SessionStart hook for ambient project context"
```

### Task 9: Update hooks.json with SessionStart entry

**Files:**
- Modify: `hooks/hooks.json`

- [ ] **Step 1: Replace hooks.json content**

Replace the entire content of `hooks/hooks.json` with:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "scripts/platform-context.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Reminder: Run tests and self-review before committing'"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -m json.tool hooks/hooks.json`

Expected: Pretty-printed valid JSON

- [ ] **Step 3: Run hook tests to verify GREEN**

Run: `pytest tests/test_hooks.py -v`

Expected: PASS — SessionStart is now in VALID_HOOK_EVENTS

- [ ] **Step 4: Commit**

```bash
git add hooks/hooks.json
git commit -m "feat(platform-docs): add SessionStart hook to hooks.json"
```

---

## Phase 5: REFACTOR — Integration Updates

### Task 10: Add PLATFORM-DOCS pipeline to orchestrator

**Files:**
- Modify: `skills/orchestrator/SKILL.md:45-56`

- [ ] **Step 1: Add pipeline route to classification**

In `skills/orchestrator/SKILL.md`, find the classification decision tree (around line 45). It currently reads:

```
IF simple question (no code needed)        → Answer directly. STOP.
IF estimation request                      → Run estimation skill. STOP.
IF bug fix                                 → Pipeline: BUG-FIX
IF feature, < 200 lines, single domain     → Pipeline: SIMPLE-FEATURE
IF feature, complex OR multi-domain        → Pipeline: COMPLEX-FEATURE
IF architecture/design decision            → Pipeline: ARCHITECTURE
IF code review / PR review                 → Pipeline: REVIEW
IF deployment / infrastructure             → Pipeline: DEPLOY
IF new language / technology               → Pipeline: NEW-TECH
IF independent sub-tasks can run parallel  → Pipeline: PARALLEL
```

Add one line after the estimation route:

```
IF simple question (no code needed)        → Answer directly. STOP.
IF estimation request                      → Run estimation skill. STOP.
IF platform docs / architecture audit      → Invoke platform-docs skill. STOP.
IF bug fix                                 → Pipeline: BUG-FIX
IF feature, < 200 lines, single domain     → Pipeline: SIMPLE-FEATURE
IF feature, complex OR multi-domain        → Pipeline: COMPLEX-FEATURE
IF architecture/design decision            → Pipeline: ARCHITECTURE
IF code review / PR review                 → Pipeline: REVIEW
IF deployment / infrastructure             → Pipeline: DEPLOY
IF new language / technology               → Pipeline: NEW-TECH
IF independent sub-tasks can run parallel  → Pipeline: PARALLEL
```

- [ ] **Step 2: Verify orchestrator is still under 500 lines**

Run: `wc -l skills/orchestrator/SKILL.md`

Expected: ≤ 500 lines (was 400, adding 1 line)

- [ ] **Step 3: Commit**

```bash
git add skills/orchestrator/SKILL.md
git commit -m "feat(orchestrator): add platform-docs routing to classification"
```

### Task 11: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add platform-docs to agent table**

In `CLAUDE.md`, find the agent table (around line 20). It currently has 5 rows. Add the platform-docs agent row:

Current table:

```markdown
| Agent (subagent_type) | Model | Composable Skills |
|-----------------------|-------|-------------------|
| `unicorn-team:developer` | sonnet | self-verification, testing, python, javascript, go |
| `unicorn-team:architect` | opus | pattern-transfer, code-reading, technical-debt |
| `unicorn-team:qa-security` | sonnet | security, testing |
| `unicorn-team:devops` | sonnet | domain-devops, security |
| `unicorn-team:polyglot` | opus | language-learning, pattern-transfer, code-reading |
```

Add after the polyglot row:

```markdown
| `unicorn-team:platform-docs` | opus | self-verification, code-reading, technical-debt |
```

- [ ] **Step 2: Update the opening description**

In `CLAUDE.md`, change the first paragraph from:

```markdown
Agent orchestration system for Claude Code. 5 agents + 14 skills, dual-layer
architecture where agents spawn as subprocesses with fresh 200K context windows.
```

to:

```markdown
Agent orchestration system for Claude Code. 6 agents + 15 skills, dual-layer
architecture where agents spawn as subprocesses with fresh 200K context windows.
```

- [ ] **Step 3: Add platform-docs to delegation routing table**

In `CLAUDE.md`, find the Delegation Routing section (around line 120). Add after the `Complex multi-domain` line:

```markdown
Platform docs / audit    -> unicorn-team:platform-docs
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add platform-docs agent to CLAUDE.md"
```

### Task 12: Update plugin.json and validate.sh

**Files:**
- Modify: `.claude-plugin/plugin.json`
- Modify: `scripts/validate.sh:33-36`

- [ ] **Step 1: Bump plugin version and update description**

In `.claude-plugin/plugin.json`, change:

```json
  "version": "2.2.0",
  "description": "Agent orchestration system with 5 subprocess agents and 14 composable skills encoding the hidden 80% of software engineering expertise. Agents spawn with fresh 200K context windows for true context isolation.",
```

to:

```json
  "version": "2.3.0",
  "description": "Agent orchestration system with 6 subprocess agents and 15 composable skills encoding the hidden 80% of software engineering expertise. Agents spawn with fresh 200K context windows for true context isolation.",
```

- [ ] **Step 2: Fix validate.sh skill count**

In `scripts/validate.sh`, change lines 33-36 from:

```bash
# 2. Count skills (13 composable skills; 5 agent protocols are inlined in agents/)
echo -n "  Skills count (expect 13)... "
SKILL_COUNT=$(find "$PROJECT_ROOT/skills" -maxdepth 2 -name "SKILL.md" | wc -l)
if [ "$SKILL_COUNT" -eq 13 ]; then
```

to:

```bash
# 2. Count skills (15 composable skills; 6 agent protocols are inlined in agents/)
echo -n "  Skills count (expect 15)... "
SKILL_COUNT=$(find "$PROJECT_ROOT/skills" -maxdepth 2 -name "SKILL.md" | wc -l)
if [ "$SKILL_COUNT" -eq 15 ]; then
```

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json scripts/validate.sh
git commit -m "chore: bump version to 2.3.0, fix validate.sh skill count"
```

### Task 13: Run full test suite and validate

**Files:** (none — verification only)

- [ ] **Step 1: Run all tests**

Run: `cd /Users/michaelhalagan/src/Libs/unicorn-team && pytest tests/ -v`

Expected: ALL PASS — 6 agents, 15 skills, valid hooks, executable scripts

- [ ] **Step 2: Run validate.sh**

Run: `./scripts/validate.sh`

Expected: All 7 checks pass with green checkmarks

- [ ] **Step 3: Verify no regressions**

Run: `pytest tests/ -v --tb=short 2>&1 | tail -20`

Expected: All tests passed, 0 failures, 0 errors

---

## Phase 6: Lai-platform-docs Changes

### Task 14: Create platform-docs.yaml manifest

**Files:**
- Create: `/Users/michaelhalagan/src/Architecture/lai-platform-docs/platform-docs.yaml`

- [ ] **Step 1: Write the manifest**

Create `/Users/michaelhalagan/src/Architecture/lai-platform-docs/platform-docs.yaml`:

```yaml
name: "LocalAI Platform"
id: "localai"

repos:
  agentcore:
    path: "/Users/michaelhalagan/src/Agents/lai-aws-bedrock-agentcore-python"
    dev_branch: "main"
    label: "Backend agent, CDK, gateway, Cedar"
  frontend-public:
    path: "/Users/michaelhalagan/src/UI/lai-localai-home"
    dev_branch: "development"
    label: "Public frontend"
  frontend-platform:
    path: "/Users/michaelhalagan/src/UI/localai-chat-amplify"
    dev_branch: "development"
    label: "Platform frontend, admin dashboard"
  mcp-server:
    path: "/Users/michaelhalagan/src/MCPs/lai-general-mcps"
    dev_branch: "main"
    label: "MCP server (10 tools)"

directories:
  reports: "current-state/"
  phases: "implementation/phases/"
  decisions: "decisions/"
  backlog: "backlog/"
  architecture: "architecture/"
  checklists: "checklists/"
  patterns: "implementation/patterns/"

report_formats:
  current_state: "CURRENT_STATE-{YYYYMMDD-HHMM}.md"
  phase_check: "PHASE_CHECK-{YYYYMMDD-HHMM}.md"
  sync_check: "SYNC_CHECK-{YYYYMMDD-HHMM}.md"
  mvp_check: "CURRENT_STATE_MVP-{YYYYMMDD-HHMM}.md"

report_subdirs:
  agentcore: "agentcore/"
  frontend-public: "frontend-public/"
  frontend-platform: "frontend-platform/"
  mcp-server: "mcp-server/"
  platform: "platform/"

entry_point: "CLAUDE.md"
```

- [ ] **Step 2: Verify manifest is valid YAML**

Run: `cd /Users/michaelhalagan/src/Architecture/lai-platform-docs && python3 -c "import yaml; yaml.safe_load(open('platform-docs.yaml')); print('Valid YAML')" 2>/dev/null || python3 -c "print('PyYAML not installed — verify manually')" `

Expected: "Valid YAML" or manual verification that the YAML is well-formed

- [ ] **Step 3: Commit**

```bash
cd /Users/michaelhalagan/src/Architecture/lai-platform-docs
git add platform-docs.yaml
git commit -m "feat: add platform-docs.yaml manifest for unicorn-team integration"
```

### Task 15: Remove 4 stale skills

**Files:**
- Delete: `.claude/skills/platform-architecture/`
- Delete: `.claude/skills/streaming-patterns/`
- Delete: `.claude/skills/dual-mode-auth/`
- Delete: `.claude/skills/mvp-plan-sync/`

- [ ] **Step 1: Remove the 4 skill directories**

Run:

```bash
cd /Users/michaelhalagan/src/Architecture/lai-platform-docs
rm -rf .claude/skills/platform-architecture
rm -rf .claude/skills/streaming-patterns
rm -rf .claude/skills/dual-mode-auth
rm -rf .claude/skills/mvp-plan-sync
```

- [ ] **Step 2: Verify remaining skills**

Run: `ls -la .claude/skills/`

Expected: Only `docs-sync-review/`, `stripe-best-practices` (symlink), and `upgrade-stripe` (symlink) remain

- [ ] **Step 3: Commit**

```bash
git add -A .claude/skills/
git commit -m "refactor: remove 4 stale skills subsumed by unicorn-team:platform-docs agent"
```

### Task 16: Refresh docs-sync-review skill

**Files:**
- Modify: `.claude/skills/docs-sync-review/SKILL.md`

- [ ] **Step 1: Add frontmatter to docs-sync-review**

The current file has no YAML frontmatter (it starts with `# Docs Sync Review`). Add frontmatter at the top:

Prepend to `.claude/skills/docs-sync-review/SKILL.md`:

```markdown
---
name: docs-sync-review
description: >-
  Review guidance for automated documentation updates triggered by code changes
  in platform repos. ALWAYS trigger on "docs sync", "doc update from code",
  "automated docs", "sync review", "PR triggered docs". Use when reviewing or
  generating documentation updates caused by source repo merges.
  Different from platform-docs which handles manual architecture audits.
---

```

Keep the existing body content unchanged below the frontmatter.

- [ ] **Step 2: Verify**

Run: `head -10 .claude/skills/docs-sync-review/SKILL.md`

Expected: YAML frontmatter block with `name:` and `description:` fields

- [ ] **Step 3: Commit**

```bash
cd /Users/michaelhalagan/src/Architecture/lai-platform-docs
git add .claude/skills/docs-sync-review/SKILL.md
git commit -m "refactor: add frontmatter to docs-sync-review skill"
```

### Task 17: Update lai-platform-docs CLAUDE.md

**Files:**
- Modify: `/Users/michaelhalagan/src/Architecture/lai-platform-docs/CLAUDE.md`

- [ ] **Step 1: Update Skills section**

In `CLAUDE.md`, find the Skills table (around line 302). Replace:

```markdown
## Skills

| Skill | Description |
|-------|-------------|
| `platform-architecture` | Quick reference to architectural decisions and patterns |
| `streaming-patterns` | Event flow, coalescing, WebSocket protocol patterns |
| `dual-mode-auth` | PUBLIC vs PLATFORM mode authentication differences |
| `mvp-plan-sync` | Patterns for keeping MVP plans in sync |
| `docs-sync-review` | Review guidance for automated doc updates from code changes |
```

with:

```markdown
## Skills

| Skill | Description |
|-------|-------------|
| `docs-sync-review` | Review guidance for automated doc updates from code changes |

> **Note:** Architecture reference skills (`platform-architecture`, `streaming-patterns`,
> `dual-mode-auth`, `mvp-plan-sync`) have been replaced by the `unicorn-team:platform-docs`
> agent, which reads architecture docs at runtime for always-current information.
> Install the [unicorn-team](https://github.com/aj-geddes/unicorn-team) plugin to use it.
```

- [ ] **Step 2: Commit**

```bash
cd /Users/michaelhalagan/src/Architecture/lai-platform-docs
git add CLAUDE.md
git commit -m "docs: update skills section for unicorn-team:platform-docs integration"
```

---

## Phase 7: User Setup

### Task 18: Create platform-docs registry

**Files:**
- Create: `~/.claude/platform-docs-registry.json`

- [ ] **Step 1: Create the registry file**

Create `~/.claude/platform-docs-registry.json`:

```json
{
  "projects": {
    "localai": {
      "path": "/Users/michaelhalagan/src/Architecture/lai-platform-docs",
      "name": "LocalAI Platform"
    }
  },
  "active": "localai"
}
```

- [ ] **Step 2: Verify the registry is valid JSON**

Run: `python3 -m json.tool ~/.claude/platform-docs-registry.json`

Expected: Pretty-printed valid JSON

- [ ] **Step 3: Verify end-to-end — hook script reads registry**

Run: `/Users/michaelhalagan/src/Libs/unicorn-team/scripts/platform-context.sh`

Expected: JSON output with `additionalContext` containing "Active platform-docs project: LocalAI Platform"

---

## Phase 8: End-to-End Verification

### Task 19: Final verification

**Files:** (none — verification only)

- [ ] **Step 1: Run unicorn-team full test suite**

Run: `cd /Users/michaelhalagan/src/Libs/unicorn-team && pytest tests/ -v`

Expected: ALL PASS

- [ ] **Step 2: Run validate.sh**

Run: `./scripts/validate.sh`

Expected: All checks pass

- [ ] **Step 3: Verify skill is discoverable**

Run: `ls skills/*/SKILL.md | wc -l`

Expected: `15`

- [ ] **Step 4: Verify agent is discoverable**

Run: `ls agents/*.md | wc -l`

Expected: `6`

- [ ] **Step 5: Verify hook fires correctly**

Run: `scripts/platform-context.sh | python3 -m json.tool`

Expected: Valid JSON with `additionalContext` field

- [ ] **Step 6: Verify lai-platform-docs manifest**

Run: `ls /Users/michaelhalagan/src/Architecture/lai-platform-docs/platform-docs.yaml`

Expected: File exists

- [ ] **Step 7: Verify stale skills removed**

Run: `ls /Users/michaelhalagan/src/Architecture/lai-platform-docs/.claude/skills/`

Expected: Only `docs-sync-review/`, `stripe-best-practices`, `upgrade-stripe`
