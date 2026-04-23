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

The following additional directories are optional. If present in the manifest,
the `context-read` (deep tier) and `deviation-check` operations will use them:

```yaml
directories:
  # ... required fields above ...
  checklists: "checklists/"          # Used by deviation-check for completable items
  patterns: "implementation/patterns/" # Used by context-read deep tier
```

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
  checklists: "checklists/"
  patterns: "implementation/patterns/"
```
