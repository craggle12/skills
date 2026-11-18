---
name: to-tasks
description: Break a plan, spec, PRD, or selected user stories into implementation tasks in the project's local kanban.json using tracer-bullet vertical slices. Use when planning implementation for selected stories or a sprint while retaining story ownership and spec coverage.
---

# To Tasks

Use this skill to break a PRD/Issue or other context driven list of work into kanban style tasks

Break a plan into independently-grabbable tasks using vertical slices in json format. Publish to the local project's `kanban.json`; do not create Azure DevOps Tasks or change sprint assignments.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments. Context can be from a prd file too 

Confirm the target repository from the supplied context before reading or writing its board. Do not assume the current directory is the project root.

#### Select the scope

- **Whole-plan mode:** When the user explicitly requests the whole plan, spec, or PRD, break down that scope as before. A standalone spec request does not require a story pack.
- **Selected-story mode:** When given a story pack, selected story references, or a sprint selection, use only the selected stories as the scope boundary. Read their full descriptions, acceptance criteria, dependencies, and relevant supporting spec sections.
- Use selections already agreed in the conversation. If a story pack or sprint is supplied without a clear selection, ask which stories to break down; do not silently process the entire spec. Do not infer sprint membership from story order or invent tracker IDs.
- Treat the original spec as supporting detail and shared constraints, not permission to expand beyond the selected stories. Flag material contradictions between the story and spec instead of silently choosing one.
- Identify missing prerequisites and dependencies on unselected stories separately. Do not generate tasks for those stories unless the user expands the selection. Show blocked work as blocked rather than claiming it is immediately actionable.
- If the selected story lacks enough detail for implementation, identify the gap and ask for the missing detail. A title-only grouping is not a substitute for acceptance criteria.

Use stable draft story references such as S1, or real Azure IDs/URLs when supplied or verified. An Azure connection is not required when the user provides the story text or a local story pack.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices and map spec coverage

#### Rules

- Each task must touch a maximum of 4 files. If a slice would require changes to more than 4 files, split it into multiple tasks.
- Inspect relevant code and existing board tasks enough to identify plausible file paths, prerequisite work, and overlap. Do not duplicate work already covered on the board.
- In selected-story mode, give every task one primary owning story and identify the acceptance criteria it contributes to. Preserve any existing criterion labels; otherwise use descriptive references without altering the source.
- Assign shared implementation once, with other tasks depending on it. Keep security and correctness constraints in every affected slice from the first usable increment.
- State dependencies and delivery order. Task size limits govern implementation tasks, not the size of the parent User Stories.

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

In selected-story mode, include the owning story reference/title, covered acceptance criteria, and dependencies in each task paragraph before its final "After this task" sentence. Also name the story pack and supporting spec so each task can be understood outside this conversation.

#### Map spec requirements to tests

In the same message as the slices above (don't wait for approval first), build a coverage table so the user can see whether the spec is actually covered by tests, and whether those tests prove behavior rather than implementation.

For each spec requirement, identify the test that proves it — an existing test in the repo, or one implied by the drafted task slices if it doesn't exist yet. Present the mapping as a table:

In selected-story mode, map every selected acceptance criterion and relevant supporting requirement, not the whole spec. Use this table instead:

| Story / acceptance criterion | Supporting spec requirement | Task(s) | Test (existing or proposed) | Behaviour being proven | How it's observed | Implementation-coupled? |
|---|---|---|---|---|---|---|

Label proposed tests explicitly. Distinguish tests inspected from tests actually run. Identify requirements outside the selection as excluded from this breakdown, not as coverage gaps. Flag selected requirements with no task or acceptance evidence as genuine gaps. For documentation or structural constraints that are not sensibly proved by a behaviour test, name the appropriate verification instead of inventing a test.

In whole-plan mode, use:

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

Include the selected stories, excluded prerequisites, target board path, and planned completed-task/progress cleanup in the proposal so approval covers the actual board update.

Wait for explicit approval before proceeding to step 4.

### 4. Reset completed work before publishing

Before adding the newly approved slices, clear out finished work so the board only reflects current, actionable tasks:

- In `kanban.json`, remove every task object whose `"passes"` field is `true`. Keep tasks where `passes` is `false`. Write the filtered `tasks` array back to `kanban.json`.
- If a `PROGRESS.md` file exists in the repo root, clear its contents (empty the file) since it tracked progress on the now-cleared tasks.

### 5. Publish the issues to the kanban file 

For each approved slice, publish a new tasks using the /add-task skill format create the tasks in kanban.json file

Read and follow the available `add-task` skill and existing board schema. In selected-story mode, preserve the owning story reference/title, source story pack/spec, criterion references, and dependencies inside the task's existing description/steps fields. Do not add unsupported JSON fields or change the board schema just to store story metadata.

Keep unfinished existing tasks and unrelated board metadata intact. Avoid reusing IDs removed during cleanup by recording the highest existing task number before filtering. Verify valid JSON, unique IDs, the four-file limit, and story traceability after publishing. Report the added task IDs grouped by owning story, along with unresolved blockers. Approval to publish local tasks does not authorize Azure writes.

## Acceptance criteria

- [ ] Tasks cover the requested plan or selected stories without silently expanding scope.
- [ ] Each selected-story task preserves its owner, source, acceptance references, and dependencies.
- [ ] Coverage distinguishes proposed tests, genuine gaps, and excluded work.
- [ ] Approved tasks are published to the correct local kanban with valid JSON and no duplicate IDs.

