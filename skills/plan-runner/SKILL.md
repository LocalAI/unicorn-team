---
name: plan-runner
description: >-
  Execute implementation plans by feeding tasks one at a time to the orchestrator.
  ALWAYS trigger on "run plan", "execute plan", "plan runner", "run the plan",
  "start plan", "resume plan", "plan status", "plan sequence", "next plan".
  Use when executing superpowers-format plans or sequencing multiple plans.
  Different from orchestrator which handles individual tasks — this skill
  handles plan-level sequencing, prerequisite checking, and checkpoint tracking.
argument-hint: "[plan-file-path]"
allowed-tools: "Read Write Edit Grep Glob Bash(find *) Bash(git *) Bash(wc *) Bash(grep *)"
---

# Plan Runner

Execute implementation plans by extracting tasks and feeding them one at a time
to the orchestrator. Handles single plans and multi-plan sequences with
prerequisite checking and checkpoint-based resumption.

## How It Works

```
plan-runner reads plan file
  → detect: single plan or master plan with sequence table?
  → IF master plan: extract ordered sub-plan paths
  → FOR each plan (or the single plan):
      → check prerequisites (prior plan completion)
      → scan for first unchecked task (resume point)
      → FOR each unchecked task:
          → extract task text + context
          → invoke orchestrator with task description
          → on success: mark checkbox [x] in plan file, commit
          → on failure: stop, report to user
      → report plan completion
  → next plan (if sequenced)
```

## Invocation

```
/unicorn-team:plan-runner path/to/plan.md           # Execute single plan
/unicorn-team:plan-runner path/to/master-plan.md     # Execute plan sequence
/unicorn-team:plan-runner status path/to/plan.md     # Check completion status
```

## Step 1: Load and Detect Plan Type

Read the plan file. Determine if it's:

**Single plan** — has `### Task` headers with checkbox steps.
Proceed directly to Step 3.

**Master plan** — has a sequence table with links to sub-plan files.
Detect by looking for a markdown table with plan file references
(e.g., `[execution-plan-1-...](./path.md)`). Extract the ordered
list of sub-plan paths. Proceed to Step 2.

## Step 2: Sequence Sub-Plans (Master Plan Only)

For each sub-plan in the sequence table (top to bottom):

```
1. Read the sub-plan file.
2. Check "Prerequisites:" header.
   → If prerequisites reference another plan, read that plan.
   → Count its checkboxes: checked vs total.
   → All checked? → Prerequisites met. Continue.
   → Some unchecked? → STOP. Report: "Plan N blocked — Plan M
     is {X}% complete ({Y}/{Z} tasks). Complete it first."
3. Execute the sub-plan (Step 3).
4. After completion, report and move to next sub-plan.
```

Between plans, report to user:

```
Plan 1: Repo Cleanup          ████████████ 100% (9/9)  ✓
Plan 2: Infrastructure         Starting...
```

## Step 3: Execute a Single Plan

Read the plan file. Find all task headers matching `### Task` pattern.
For each task, count its checkbox steps (`- [ ]` and `- [x]`).

**Find resume point:** Scan tasks top-to-bottom. The first task with any
unchecked `- [ ]` step is where execution resumes. Tasks where all steps
are `- [x]` are already complete — skip them.

For each unchecked task:

```
1. Extract the full task text (everything from ### Task header to the
   next ### Task header or ## Phase header).

2. Extract key metadata from the task:
   - Repo path (from **Repo:** line)
   - Files involved (from **Files:** section)
   - Dependencies (from **Depends on:** line)

3. Build an orchestrator request from the task:
   "Execute this task from the implementation plan:

    [full task text including all steps]

    Repo: [repo path]
    Follow every step exactly. Run all verification commands.
    Commit with the exact messages specified."

4. Invoke the orchestrator skill with this request.
   The orchestrator will:
   - Classify (likely SIMPLE-FEATURE, COMPLEX-FEATURE, or DEPLOY)
   - Enrich with docs context (Step 1.5, if repo is in manifest)
   - Route to the right agents
   - Gate quality
   - CEO QC (for complex tasks)
   - Double-check

5. On success: mark all checkbox steps in the task as [x] in the
   plan file. Write the file. Commit:
   git add <plan-file>
   git commit -m "plan: complete task [task name]"

6. On failure: STOP execution. Report which task failed, what the
   error was, and which step it failed on. Do NOT continue to the
   next task.
```

## Step 4: Report Completion

After all tasks in a plan are checked:

```
## Plan Complete: [plan name]

Tasks: [N/N] complete
Repos touched: [list]
Duration: [approximate]

Next: [path to next plan, or "Sequence complete"]
```

If executing a master plan sequence, return to Step 2 for the next sub-plan.

## `status` Command

When invoked with `status`:

```
/unicorn-team:plan-runner status path/to/plan.md
```

Read the plan (or master plan). For each plan/sub-plan, count checkboxes:

```
Platform Execution Plan — Overall Progress

Plan 1: Repo Cleanup           ████████████ 100%  (9/9 tasks)
Plan 2: Infrastructure          ████░░░░░░░░  35%  (8/23 tasks)
Plan 3: Standards               ░░░░░░░░░░░░   0%  (blocked by Plan 2)
Plan 4: Gaps & A2A              ░░░░░░░░░░░░   0%  (blocked by Plans 2+3)

Current: Plan 2, Task C.4 (Fix Content Gen UI)
Next unchecked step: Step 3 — Run tests, confirm red
```

## Checkpoint Mechanism

The plan markdown file IS the checkpoint. Checked boxes (`- [x]`) persist
across sessions. When plan-runner starts, it reads the file and resumes
from the first unchecked step. No external state needed.

This means:
- Session ends mid-plan → next session runs same command → resumes
- Manual edits to checkboxes are respected
- Multiple people can track progress by reading the plan file

## Edge Cases

**Plan file not found:** Error with exact path tried.

**All tasks already checked:** Report "Plan already complete" and skip.

**Task fails 3 times:** Stop, report to user. Do not continue sequence.

**Orchestrator can't classify task:** The orchestrator's error recovery
handles this — it asks the user for clarification. Plan-runner waits.

**Prerequisites not met:** Report which prerequisite plan is incomplete
with percentage. Do not proceed.

**Task has human decision points:** If a task step says "Ask the user"
or "MANUAL STEP," the orchestrator will surface this. Plan-runner waits
for the orchestrator to return.
