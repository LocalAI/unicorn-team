---
name: platform-docs
description: >-
  Platform documentation operations across multiple projects. ALWAYS trigger on
  "platform docs", "current state", "whats next", "check phase", "ADR",
  "architecture review", "platform status", "check sync", "check drift", "docs drift", "technical debt backlog",
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
| `register <id> <path>` | Direct | Add a new project (validates manifest) |
| `unregister <id>` | Direct | Remove a project from registry |
| `status` | Direct | Show active project health summary |
| `current-state [repo]` | Agent | Full architecture audit |
| `current-state-all` | Agent | Parallel audit of all repos |
| `whats-next [repo]` | Agent | Next work items and blockers |
| `check-phase [phase] [repo]` | Agent | Phase readiness verification |
| `check-sync` | Agent | Internal docs consistency check |
| `review-proposal [path]` | Agent | Evaluate feature proposal |
| (no args / help) | Direct | Show this command list |

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
