---
name: tdd
description: Use when the user asks for test-driven development, TDD, red-green-refactor, one behavior test at a time, or wants changes made in small approval-gated slices where a failing behavior-focused test is written before implementation. Applies to coding tasks in any language when tests can reasonably drive behavior.
---

# TDD

## Core Workflow

Use one behavior test red-green-refactor slices. One test may use several inputs, assertions, or table cases when they all describe the same behavior.

Default ownership of the test loop:

- Codex writes the red behavior test directly and reports the exact command. Do not print the patch or diff by default unless the user asks for it.
- The user runs the test and confirms the red result.
- Codex writes only the implementation needed to make that behavior pass after the user asks to green it.
- The user reruns the focused test and reports the result.
- Codex refactors only after the user confirms green and the refactor is required or requested.
- Codex must not run tests, syntax checks, compile checks, format checks, or other verification commands unless the user explicitly asks Codex to run them.

1. Inspect only the files needed to understand the next behavior.
2. Identify the smallest next behavior and the single test that should express that behavior.
3. Prefer behavior-focused tests over implementation-detail tests. A table-driven test is acceptable when every row exercises the same rule.
4. Prefer shallow public interfaces for module tests. Test the module's public behavior through one or two public entry points rather than testing every helper, constant, field, or intermediate struct.
5. If tests start multiplying around internal fields or helper functions, pause and redesign the public API so one behavior test can cover the useful contract.
6. Explain what that test does in plain language before or immediately after adding it.
7. Add only that one behavior test.
8. Give the exact focused test command and wait for the user to run it.
9. Treat the red state as confirmed only after the user reports it. If the user reports that the test unexpectedly passes, say so and do not invent implementation work.
10. After the user asks to green it, apply the smallest implementation change needed to make that one behavior pass, according to the current collaboration mode. Do not print a patch or diff by default unless the user asks for it.
11. Apply implementation only after approval when approval gates are active.
12. Format the touched files when appropriate.
13. Give the exact focused test command and wait for the user to run it.
14. Repeat with the next behavior test.
15. Refactor only after the current behavior is green, and keep refactors separate from new behavior unless the user approves combining them.

## Approval Discipline

- Do not batch unrelated behaviors unless the user explicitly asks for a larger slice.
- Do not split one coherent behavior into artificial one-assertion tests.
- Do not expose internals just so they can be tested; prefer testing through the shallow public API.
- Do not add field-by-field tests when a public behavior test can cover the same contract.
- Do not write implementation before the red test is accepted.
- Do not edit files outside the current approved chunk or file list.
- If the next needed change requires a new file or an out-of-scope file, stop and ask.
- Do not stage or commit unless the user explicitly approves.
- Do not run verification commands unless the user explicitly asks Codex to run them.

## Test Selection

Choose tests in this order:

1. A focused public API behavior test for the module.
2. A protocol-shape test when the public contract is serialized data.
3. A narrow integration test when behavior crosses module boundaries.
4. A regression test for existing behavior that must not be disturbed.

Prefer a test that fails for one clear behavioral reason. Avoid tests that require network access, secrets, live writes, or broad environment setup unless the user explicitly requests that level.

## Reporting Format

For each red test, report:

- Test file.
- Files changed, kept to the approved one-file slice unless the user approved more.
- Test name.
- What the test does.
- Why it should fail now.
- Exact command to run, if the user is running tests.
- State that Codex has not run the command unless explicitly asked.
- Proposed green implementation only after the red state is known or reasonably established.

For each green implementation, report:

- Files changed.
- Behavior added.
- Formatting performed.
- Test command left for the user, unless the user explicitly asked Codex to run it.

## Refactor Step

After a behavior is green, check whether the implementation has meaningful duplication, confusing names, or awkward structure. If there is no clear improvement, say no refactor is needed. If there is, propose a separate refactor patch and keep behavior unchanged.
