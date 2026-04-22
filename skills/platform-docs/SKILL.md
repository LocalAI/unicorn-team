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
