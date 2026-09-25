---
name: to-tasks
description: Break a plan, spec, or PRD into independently-grabbable tasks on the project kanban board using tracer-bullet vertical slices. Use when user wants to convert a plan tasks to implement
---

# To Tasks

Use this skill to break a PRD/Issue or other context driven list of work into kanban style tasks

Break a plan into independently-grabbable tasks using vertical slices in json format

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments. Context can be from a prd file too 

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices and map spec coverage

#### Rules

- Each task must touch a maximum of 4 files. If a slice would require changes to more than 4 files, split it into multiple tasks.

#### What to build

A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation.

Present the proposed slices to the user using this exact format:

```
**TASK-XX — category-name**
One paragraph describing what this slice builds end-to-end. Include key constraints or decisions.
Finish with: "After this task, [what is usable/observable]."

---

**TASK-XX — next-category**
...
```

#### Map spec requirements to tests

In the same message as the slices above (don't wait for approval first), build a coverage table so the user can see whether the spec is actually covered by tests, and whether those tests prove behavior rather than implementation.

For each spec requirement, identify the test that proves it — an existing test in the repo, or one implied by the drafted task slices if it doesn't exist yet. Present the mapping as a table:

| Spec requirement | Test | Behaviour being proven | How it's observed | Implementation-coupled? |
|---|---|---|---|---|

Fill each column like this:
- **Behaviour being proven**: what an external caller/user observes, in plain language — never a description of internal mechanics.
- **How it's observed**: the observation mechanism — a return value, a state check, a visible side effect. Not "calls X" or "spies on Y".
- **Implementation-coupled?**: `Yes ⚠️` if the test asserts on a private function, internal state, or a call count/mock (`assert_called_once`, `.mock_calls`, spying on an internal method) rather than on observable behavior. Otherwise `No`. Test what the module does, not how it does it.

After the table, explicitly call out:
- Spec requirements with no matching test (a coverage gap).
- Any test marked `Yes ⚠️`, since it tests implementation rather than behaviour and should be rewritten to assert on observable behavior instead.

Then ask one combined question covering both the slices and the coverage table: "Are you happy with this split and test coverage, or would you like to adjust anything?"

Wait for explicit approval before proceeding to step 4.

### 4. Reset completed work before publishing

Before adding the newly approved slices, clear out finished work so the board only reflects current, actionable tasks:

- In `kanban.json`, remove every task object whose `"passes"` field is `true`. Keep tasks where `passes` is `false`. Write the filtered `tasks` array back to `kanban.json`.
- If a `PROGRESS.md` file exists in the repo root, clear its contents (empty the file) since it tracked progress on the now-cleared tasks.

### 5. Publish the issues to the kanban file 

For each approved slice, publish a new tasks using the /add-task skill format create the tasks in kanban.json file

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

