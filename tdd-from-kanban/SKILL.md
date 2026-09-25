---
name: tdd-from-kanban
description: Use when the user asks to work the kanban board test-first, pick up the next kanban task with TDD, or run red-green-refactor against kanban.json. Same red-green-refactor discipline as the tdd skill, except the next behavior comes from a non-passed task in kanban.json instead of ad-hoc conversation, and findings/gotchas get logged to PROGRESS.md as work proceeds.
---

# TDD From Kanban

Everything in the `tdd` skill applies unchanged: one behavior test per
red-green-refactor slice, approval gates before implementation, no running
verification commands unless explicitly asked. The only differences are
where the next behavior comes from and that progress gets logged as you go.

## Communication Style

If the `caveman` skill is available, invoke it and report in caveman mode
for the duration of this workflow. The reporting format below still
applies -- every required item is still reported, just compressed. Keep
these verbatim and uncompressed regardless of mode:

- Test commands given to the user.
- File paths, test names, task IDs, and `kanban.json` field values.
- Text written to files: test code, implementation, PROGRESS.md entries,
  and kanban updates are always written in normal prose/code.

If `caveman` is not available, report normally.

## Task Selection

1. Read `kanban.json` in the repo root.
2. Unless the user names a specific task ID, pick the first task in
   `tasks` with `"passes": false`.
3. If every task has `"passes": true`, say so and stop -- do not invent a
   task.
4. Before writing any test, state the picked task's `id`, `category`,
   `description`, and `acceptance_criteria` back to the user so the scope
   is confirmed up front.
5. The task's `steps` and `tests` arrays are the source for behavior
   slices -- work through them in order, one behavior test at a time, the
   same way the `tdd` skill would work through user-described behaviors.
   Do not add behavior the task doesn't ask for.
6. If the task is ambiguous, its `files` list looks incomplete, or it
   depends on another task that isn't `passes: true` yet, stop and ask
   rather than guessing.

## PROGRESS.md Logging

`PROGRESS.md` resets per kanban list -- finding it empty or short at the
start of a task is expected, not data loss. Do not restore prior git
history into it; just append.

- Before the first test of a task, append a new section header:
  `## Ralph-<TASK-ID>: <category>` (matches the existing convention in
  this file).
- As work proceeds -- not only at the end -- append short bullet notes
  under that section for anything a future agent would want to know
  before touching this task again: findings (e.g. "implementation already
  existed, only kanban bookkeeping was stale"), gotchas (e.g. a flag that
  turns out to be a no-op, an MT5/engine parity quirk, a fixture that
  needs a specific seed), and any deviation from the task's `steps`.
- Keep entries factual and specific enough to act on later; skip restating
  what the diff already makes obvious.
- When the task's acceptance criteria are verified green (user-confirmed,
  full suite passing per the task's `tests`), append a **Status:** line
  stating the task is done, then update `kanban.json` to set that task's
  `"passes"` to `true`. Do not flip `passes` to `true` on partial/red
  progress.

## Core Workflow

1. Inspect only the files needed to understand the next behavior in the
   picked task's `steps`/`tests`.
2. Identify the smallest next behavior from the task and the single test
   that should express it.
3. Prefer behavior-focused tests over implementation-detail tests. A
   table-driven test is acceptable when every row exercises the same rule.
4. Prefer shallow public interfaces for module tests. Test the module's
   public behavior through one or two public entry points rather than
   testing every helper, constant, field, or intermediate struct.
5. If tests start multiplying around internal fields or helper functions,
   pause and redesign the public API so one behavior test can cover the
   useful contract.
6. Explain what that test does in plain language before or immediately
   after adding it.
7. Add only that one behavior test.
8. Give the exact focused test command and wait for the user to run it.
9. Treat the red state as confirmed only after the user reports it. If the
   user reports the test unexpectedly passes, say so, note it in
   PROGRESS.md as a finding, and do not invent implementation work.
10. After the user asks to green it, apply the smallest implementation
    change needed to make that one behavior pass. Do not print a patch or
    diff by default unless the user asks for it.
11. Apply implementation only after approval when approval gates are
    active.
12. Format the touched files when appropriate.
13. Give the exact focused test command and wait for the user to run it.
14. Log any finding or gotcha surfaced by this slice to PROGRESS.md.
15. Repeat with the next behavior test, working down the task's
    `steps`/`tests` list.
16. Refactor only after the current behavior is green, and keep refactors
    separate from new behavior unless the user approves combining them.
17. Once the task's full `tests` list is green and acceptance criteria are
    met, write the PROGRESS.md **Status:** line and flip `passes` to
    `true` in `kanban.json`.

## Approval Discipline

- Do not batch unrelated behaviors unless the user explicitly asks for a
  larger slice.
- Do not split one coherent behavior into artificial one-assertion tests.
- Do not expose internals just so they can be tested; prefer testing
  through the shallow public API.
- Do not add field-by-field tests when a public behavior test can cover
  the same contract.
- Do not write implementation before the red test is accepted.
- Do not edit files outside the current task's `files` list unless the
  user approves expanding scope.
- If the next needed change requires a new file or an out-of-scope file,
  stop and ask.
- Do not stage or commit unless the user explicitly approves.
- Do not run verification commands unless the user explicitly asks for it.
- Do not flip a task's `passes` to `true` without the user's confirmed
  green result.

## Test Selection

Choose tests in this order:

1. A focused public API behavior test for the module, per the task's
   `tests` entries.
2. A protocol-shape test when the public contract is serialized data.
3. A narrow integration test when behavior crosses module boundaries.
4. A regression test for existing behavior that must not be disturbed.

Prefer a test that fails for one clear behavioral reason. Avoid tests that
require network access, secrets, live writes, or broad environment setup
unless the task or user explicitly calls for that level.

## Reporting Format

For each red test, report:

- Test file.
- Files changed, kept to the task's `files` list unless the user approved
  more.
- Test name.
- What the test does.
- Why it should fail now.
- Exact command to run, if the user is running tests.
- State that verification hasn't been run unless explicitly asked.
- Proposed green implementation only after the red state is known or
  reasonably established.

For each green implementation, report:

- Files changed.
- Behavior added.
- Formatting performed.
- Test command left for the user, unless the user explicitly asked for it
  to be run.
- Any PROGRESS.md entry just appended.

## Refactor Step

After a behavior is green, check whether the implementation has
meaningful duplication, confusing names, or awkward structure. If there is
no clear improvement, say no refactor is needed. If there is, propose a
separate refactor patch and keep behavior unchanged.
