---
name: hvs-skill-buddy
description: >-
  HVS Skill Buddy is the meta-skill for the entire HVS skill ecosystem. It
  keeps skills current with the latest Anthropic patterns, audits the skill
  library for drift and inconsistency, and creates new skills that fit the HVS
  system standard. ALWAYS trigger when the user mentions "skill buddy", "audit
  my skills", "skill drift", "create a new skill", "build a skill", "update my
  skills", "skill system", "are my skills consistent", "hvs skill", "skill
  conflicts", "skill overlap", "new skill for", or any request to inspect,
  improve, create, or manage skills in the HVS library. Also trigger when
  someone asks Claude to "make a skill like my other ones" or "keep this
  consistent with my existing skills."
---

# HVS Skill Buddy

The meta-skill that keeps the HVS skill ecosystem coherent, current, and consistent.
It does three things: **audit** (find drift), **update** (stay current), and
**create** (new skills that fit the system).

## Mode Selection

Identify which mode applies from the user's request:

| User Says | Mode |
|-----------|------|
| "Audit my skills", "check for drift", "are these consistent" | → [Audit Mode](#audit-mode) |
| "What's new in skills?", "update the skill system", "self-update" | → [Self-Update Mode](#self-update-mode) |
| "Create a skill for X", "build a skill that does Y" | → [Create Mode](#create-mode) |
| "Fix this skill", "update this skill to match others" | → Audit Mode on single skill + Create Mode to rewrite |

When in doubt, **ask**. One clarifying question is better than working on the wrong thing.

---

## Audit Mode

Systematically inspect the HVS skill library for drift, overlap, and inconsistency.

### Step 1 — Inventory the Library

```bash
# List all user skills with their sizes
for skill in /mnt/skills/user/*/SKILL.md; do
  name=$(basename $(dirname "$skill"))
  lines=$(wc -l < "$skill")
  refs=$(ls "$(dirname "$skill")/references/" 2>/dev/null | wc -l | tr -d ' ')
  scripts=$(ls "$(dirname "$skill")/scripts/" 2>/dev/null | wc -l | tr -d ' ')
  echo "$name | lines=$lines | refs=$refs | scripts=$scripts"
done
```

### Step 2 — Run the Drift Checker

```bash
python3 /mnt/skills/user/hvs-skill-buddy/scripts/audit-skills.py \
  --skills-dir /mnt/skills/user \
  --standard /mnt/skills/user/hvs-skill-buddy/references/hvs-system-standard.md
```

This script checks every skill against the HVS system standard and outputs a
structured drift report. Read the report carefully before proceeding.

### Step 3 — Classify Findings

After running the checker, sort findings into three buckets:

**Critical (fix now)**
- A skill installs a tool/framework that another skill already owns (technology boundary violation)
- A skill's install commands are inconsistent with the HVS canonical form
- A skill references a file that does not exist

**Warning (fix soon)**
- Missing pre-flight check in a skill that interacts with external systems
- Description lacks trigger keywords for a common use case
- No references directory in a skill with >150 lines

**Info (nice to have)**
- Different heading styles across similar skills
- Script names don't follow the `verb-noun.sh` / `verb_noun.py` convention

### Step 4 — Report to User

Present findings as a structured table. Example format:

```
AUDIT REPORT — HVS Skill Library
Generated: [date]

CRITICAL (2)
─────────────────────────────────────────────────────────────────
hvs-user-journey-skill  | Playwright install: missing pytest-playwright
                        | Fix: pip install playwright pytest-playwright --break-system-packages

hvs-e2e-testing         | Playwright install: missing `playwright` package
                        | Fix: pip install playwright pytest-playwright --break-system-packages

WARNING (1)
─────────────────────────────────────────────────────────────────
sow-bidding             | No pre-flight check for required environment vars
                        | Suggestion: add Step 0 checking for HVS_RATE, etc.

INFO (3)
─────────────────────────────────────────────────────────────────
...

TECHNOLOGY BOUNDARIES (no violations)
─────────────────────────────────────────────────────────────────
✓ Playwright owned by: hvs-e2e-testing (all others defer to it)
✓ Docker builds owned by: docker-build-expert
...
```

### Step 5 — Fix (with permission)

For each critical finding, ask: "Want me to fix this now?" Then apply fixes using
the Create Mode template to rewrite only the affected section. Never rewrite a
full skill unless the user asks.

---

## Self-Update Mode

Keep the HVS skill system current with Anthropic's latest patterns and any
advances in the underlying technologies.

### Step 1 — Check Anthropic Skill Docs

Use web search to check for updates:

```
Search: "Anthropic Claude skills system prompt 2025 site:docs.anthropic.com"
Search: "Claude skill creator SKILL.md best practices"
Search: site:docs.claude.com skills
```

Also fetch the current skill-creator skill to compare against what's embedded here:

```bash
cat /mnt/skills/examples/skill-creator/SKILL.md | head -120
```

### Step 2 — Check Technology Currency

For each technology owned by an HVS skill, check for significant updates:

```
Search: "playwright 2025 latest version breaking changes"
Search: "pytest-playwright 2025 update"
Search: "helm 2025 best practices kubernetes"
Search: "GitHub Actions 2025 new features security"
```

Look for:
- Deprecated APIs or commands the skills still use
- New security advisories affecting patterns in the skills
- Major version bumps that change install or invocation syntax

### Step 3 — Update the System Standard

If Anthropic has changed how skills work (new frontmatter fields, new loading
behavior, new triggering mechanism), update `references/hvs-system-standard.md`
to reflect the change.

Show the diff to the user before applying it.

### Step 4 — Propagate Critical Changes

If a technology update affects multiple skills (e.g., a Playwright major version
changes install syntax), use Audit Mode to find every affected skill and queue
them for update.

---

## Create Mode

Build a new skill that fits the HVS system standard from the first line.

### Step 1 — Intake Interview

Before writing anything, answer these questions (extract from conversation or ask):

1. **What does this skill do?** (one sentence, active voice)
2. **When should it trigger?** (list 5-10 user phrases)
3. **What technology stack does it use?** (check the Technology Registry — don't
   duplicate ownership)
4. **Does a similar skill already exist?** (search `/mnt/skills/user/`)
5. **What does the output look like?** (file, report, deployed resource, etc.)
6. **Does it need scripts/automation, or is it guidance-only?**
7. **What can go wrong?** (pre-flight checks needed)

### Step 2 — Technology Boundary Check

Before writing install commands, check `references/technology-registry.md`. If
the skill needs a tool that another skill already owns:

- **Don't re-install it** — reference the owning skill instead
- Add a dependency note: `> This skill requires docker-build-expert for image builds`
- Only add install commands for tools unique to this skill

### Step 3 — Apply the HVS Skill Template

See `references/hvs-system-standard.md` for the full template. The short version:

```
SKILL_NAME/
├── SKILL.md                    # Required. Frontmatter + instructions
│   ├── YAML frontmatter        # name, description (pushy triggers)
│   ├── Mode Selection table    # (if skill has multiple modes)
│   ├── Pre-flight Check        # (if skill touches external systems)
│   ├── Phase N: ...            # Numbered phases for multi-step workflows
│   └── References section      # Pointers to files in references/
├── references/
│   ├── [topic].md              # One file per major sub-topic
│   └── ...
└── scripts/
    ├── [verb]-[noun].sh        # Shell scripts: kebab-case
    └── [verb]_[noun].py        # Python scripts: snake_case
```

**Non-negotiables for every HVS skill:**
- `--break-system-packages` on every `pip install`
- `2>/dev/null || true` on optional npm installs (never fail the pre-flight)
- Playwright install canonical form (see Technology Registry)
- Phase numbers start at 1, not 0
- Decision tables use the 3-column format: `| Situation | Approach | Reference |`
- Reports go to `/tmp/hvs-[skill-name]-[timestamp]/` to avoid clobbering

### Step 4 — Write the Skill

Follow the template. Length guidance:
- `SKILL.md`: 150–400 lines (under 500 hard limit)
- Each `references/*.md`: 50–300 lines
- Scripts: as long as needed, well-commented

### Step 5 — Consistency Check

Before delivering, verify the new skill against the standard:

```bash
python3 /mnt/skills/user/hvs-skill-buddy/scripts/audit-skills.py \
  --single /tmp/new-skill-name \
  --standard /mnt/skills/user/hvs-skill-buddy/references/hvs-system-standard.md
```

Fix any findings before handing to the user.

### Step 6 — Package and Deliver

```bash
# Copy to outputs
cp -r /tmp/new-skill-name /mnt/user-data/outputs/
```

Then use `present_files` to hand the skill directory to the user.

---

## Reference Files

| File | Contents |
|------|----------|
| `references/hvs-system-standard.md` | The canonical HVS skill template and all non-negotiable rules |
| `references/technology-registry.md` | Which skill owns which technology stack |
| `references/known-drift.md` | Tracked drift issues across the library (running log) |

Read the relevant reference file before taking action in any mode.

---

## Guiding Principles

**One owner per technology.** If docker-build-expert owns Docker, no other skill
runs its own image build logic. Skills reference each other, not duplicate.

**Fail loud in pre-flight, silent in optional deps.** Required tools fail the
workflow with a clear error. Optional enhancements use `2>/dev/null || true`.

**Consistent install patterns.** Every skill that installs Python packages uses
`--break-system-packages`. No exceptions.

**Phases, not prose.** Multi-step workflows use numbered `## Phase N` headings.
This makes sub-agent handoff deterministic.

**Reports have a home.** All output goes to `/tmp/hvs-[skill]-[timestamp]/`.
Never scatter files.

**The registry is truth.** If a technology isn't in the registry, add it before
writing install commands. If it's already there, defer to the owning skill.
