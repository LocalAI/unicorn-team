# HVS Skill Library — Known Drift Log

Running log of tracked drift issues. When hvs-skill-buddy audits the library,
confirmed issues are added here. Resolved issues are marked ✅ and retained
for history.

Format per entry:
```
[DATE] | SEVERITY | SKILL | FINDING | STATUS
```

---

## Open Issues

### CRITICAL

| Date | Skill | Finding | Status |
|------|-------|---------|--------|
| 2026-03 | `hvs-user-journey-skill` | Playwright install is `pip install playwright --break-system-packages` — missing `pytest-playwright` package | Open |
| 2026-03 | `hvs-e2e-testing` | Playwright install is `pip install pytest-playwright` — missing the `playwright` package itself | Open |
| 2026-03 | `hvs-exploratory-testing` | Optional `@playwright/cli` install uses `2>/dev/null \|\| true` ✓ but base `pip install` form includes both packages ✓ — this skill is the closest to canonical | Open (minor) |

**Canonical Playwright install** (apply to all three skills):
```bash
pip install playwright pytest-playwright --break-system-packages
playwright install --with-deps chromium
```

### WARNING

| Date | Skill | Finding | Status |
|------|-------|---------|--------|
| 2026-03 | `hvs-user-journey-skill` | No pre-flight environment check despite spawning Playwright browsers | Open |
| 2026-03 | `sow-bidding` | No pre-flight check; silently depends on HVS rate constants that could drift | Open |

### INFO

| Date | Skill | Finding | Status |
|------|-------|---------|--------|
| 2026-03 | `ml-engineering` | Uses `## Phase` structure ✓ but no pre-flight check for GPU/CUDA availability | Open |
| 2026-03 | `github-pages-designer` | Does not cross-reference `github-actions-expert` for CI/CD deploy workflows | Open |

---

## Resolved Issues

| Date | Skill | Finding | Resolution |
|------|-------|---------|------------|
| 2026-03 | `agents/developer` | Loose .md file, not in SKILL_NAME/SKILL.md directory structure | ✅ Restructured to `agents/developer/SKILL.md` with `references/` and `scripts/` |
| 2026-03 | `agents/architect` | Loose .md file (1,652 lines), massive bloat | ✅ Restructured to `agents/architect/SKILL.md` (203 lines) with 5 reference files |
| 2026-03 | `agents/qa-security` | Loose .md file, not in directory structure | ✅ Restructured to `agents/qa-security/SKILL.md` with `references/` |
| 2026-03 | `agents/devops` | Loose .md file (925 lines), oversized | ✅ Restructured to `agents/devops/SKILL.md` (159 lines) with 4 reference files |
| 2026-03 | `agents/polyglot` | Loose .md file (737 lines), oversized | ✅ Restructured to `agents/polyglot/SKILL.md` (164 lines) with 3 reference files |
| 2026-03 | `unicorn/*` (7 skills) | Teaching material instead of action instructions, oversized | ✅ All 7 skills reworked: 45-67% line reduction, decision tables over prose |
| 2026-03 | `domain/*` (5 skills) | Missing pushy trigger phrases, some oversized | ✅ All 5 skills polished: descriptions updated, content tightened |
| 2026-03 | Scripts at project root | `tdd.sh`, `self-review.sh`, `estimate.sh`, `new-language.sh` not co-located | ✅ Moved to owning skill `scripts/` directories |

---

## Audit History

| Date | Mode | Skills Checked | Critical | Warning | Info | Notes |
|------|------|---------------|----------|---------|------|-------|
| 2026-03 | Initial bootstrap | 21 | 3 | 2 | 2 | hvs-skill-buddy creation audit |
| 2026-03 | Deep rework audit | 18 | 0 | 0 | 0 | All unicorn-team skills pass clean after rework |
