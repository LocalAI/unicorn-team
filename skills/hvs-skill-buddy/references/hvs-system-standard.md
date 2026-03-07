# HVS Skill System Standard

The canonical template and rules for every skill in the HVS library.
Skills that diverge from this standard will be flagged by hvs-skill-buddy's audit.

---

## Frontmatter Standard

```yaml
---
name: skill-name                    # kebab-case, matches directory name
description: >-                     # Multi-line OK, but keep under ~80 words
  One-sentence summary of what the skill does. ALWAYS trigger on "phrase1",
  "phrase2", specific technical terms it owns, and any user-facing language
  that would indicate this skill applies. Include negative differentiators
  from similar skills ("Different from hvs-e2e-testing which requires
  pre-defined journeys — this needs only a URL.").
---
```

**Rules:**
- `name` must exactly match the directory name
- Description must include "ALWAYS trigger on" or "Use when" with explicit phrases
- Description must be "pushy" — list more triggers than you think you need
- If skill has a sibling/related skill, mention the difference in the description

---

## Directory Structure Standard

```
skill-name/
├── SKILL.md                       # Required
├── references/                    # Required if SKILL.md > 200 lines
│   └── [topic].md                 # One file per major sub-topic
├── scripts/                       # Optional; only for automatable tasks
│   ├── [verb]-[noun].sh           # Shell: kebab-case
│   └── [verb]_[noun].py           # Python: snake_case
└── assets/                        # Optional; static files (templates, icons)
    └── [name].[ext]
```

---

## SKILL.md Body Structure

### Simple skills (single workflow, < 200 lines)

```markdown
# Skill Title

One-sentence description of what this skill produces or enables.

## Workflow

### Step 1 — [Action]
...

### Step 2 — [Action]
...
```

### Complex skills (multiple modes or > 200 lines)

```markdown
# Skill Title

One-sentence description.

## Mode Selection

| User Says | Mode |
|-----------|------|
| "phrase A" | → [Mode A](#mode-a) |
| "phrase B" | → [Mode B](#mode-b) |

---

## Pre-flight Check          ← Required if touching external systems

### 1. [Check Name]
...

### 2. [Check Name]
...

---

## Phase 1: [Phase Name]    ← Numbered phases for multi-step workflows
...

## Phase 2: [Phase Name]
...

---

## Reference Files          ← At the bottom, pointer table to references/
```

---

## Non-Negotiable Rules

### Python Package Installation
```bash
# ALWAYS use --break-system-packages
pip install package-name --break-system-packages

# For Playwright (canonical form — use exactly this):
pip install playwright pytest-playwright --break-system-packages
playwright install --with-deps chromium
```

### NPM Global Installation
```bash
# Required tools: install without suppression
npm install -g tool-name

# Optional tools: never fail the pre-flight
npm install -g optional-tool 2>/dev/null || true
```

### Output Directory
```bash
# All skill outputs go here — never scatter files
OUTDIR="/tmp/hvs-$(skill-name)-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTDIR"
```

### Docker / Container Builds
> Any skill that needs to build a container image must reference `docker-build-expert`.
> Never write raw `docker build` commands in other skills.

### GitHub Actions
> Any skill that generates or modifies `.github/workflows/*.yml` must reference
> `github-actions-expert`. Never inline GHA YAML patterns in other skills.

### Kubernetes / Helm
> Any skill that deploys to Kubernetes must reference `containerized-database`
> (for databases) and/or document Helm commands aligned with the hvs-context cluster.

---

## Decision Table Format

Every decision table uses this 3-column format:

```markdown
| Situation | Approach | Reference |
|-----------|----------|-----------|
| Condition A | Do X | `references/x.md` |
| Condition B | Do Y | `references/y.md` |
```

Never use 2-column decision tables without a reference column for complex skills.

---

## Phase Numbering

- Phases start at **1**, not 0
- Use `## Phase N: Name` (not `### Phase N`, not `## N. Name`)
- Sub-steps within a phase use `### Step N.M — Name` or `### N. Name`
- Sub-agents launched in a phase use the sub-agent block pattern:

```markdown
### Sub-agent 1: [Role]

> [Task description in blockquote format — this is what gets sent to the sub-agent]
> Return a structured summary covering:
> - Item 1
> - Item 2
```

---

## Pre-flight Check Pattern

```markdown
## Pre-flight Check

### 1. [Check Name]

[What to verify and how]

```bash
# verification command
```

If [failure condition]:
> "[Clear error message explaining what's missing and what to do]"

### 2. [Next Check]
...
```

---

## Report Structure

All skills that produce reports must:
1. Write the report to `$OUTDIR/report.md` (markdown) or `$OUTDIR/report.html`
2. Include a Summary section at the top with counts (N found, N critical, N warnings)
3. Include a Timestamp line
4. Use the HVS report header format:

```markdown
# [Skill Name] Report
Generated: [timestamp]
Target: [what was analyzed]

## Summary
- Critical: N
- Warning: N  
- Info: N
- Passed: N

## Findings
...
```

---

## Skill Complexity Tiers

Use these to calibrate how much structure a skill needs:

| Tier | Lines | Phases | References | Scripts | Example |
|------|-------|--------|------------|---------|---------|
| Nano | < 100 | 0 | 0 | 0 | nano-banana-prompt, aj-writing-style |
| Standard | 100–250 | 0–2 | 1–3 | 0–1 | docker-build-expert, sow-bidding |
| Complex | 250–400 | 3–5 | 3–6 | 1–4 | github-actions-expert, ml-engineering |
| System | 400–500 | 5–8 | 5–10 | 4–8 | hvs-e2e-testing, hvs-exploratory-testing |

Do not create a System-tier skill when a Standard-tier would do.

---

## Versioning and Change Notes

Skills don't have semver, but significant changes should be noted in a comment
block at the top of SKILL.md body:

```markdown
<!-- Last reviewed: 2026-03 | Reviewed by: hvs-skill-buddy -->
<!-- Changes: Standardized Playwright install, added Phase 3 sub-agent pattern -->
```
