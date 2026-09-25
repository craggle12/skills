---
name: grill-me-to-tasks
description: Use for smaller features that need questioning but not a full spec. Grills the user on requirements, prints a short plan summary (summary, solution, implementation, acceptance, out of scope), waits for approval, then writes kanban tasks via to-tasks. Trigger when the user says grill me to tasks, grill me then make tasks, small feature straight to tasks
---

# Grill Me To Tasks

Use this skill for smaller features that do not warrant a full spec/PRD. It chains three steps: grill the user on
requirements, print a lightweight plan summary for approval, then publish kanban tasks.

Do not start implementation work while using this skill. This skill ends at published tasks.

## Process

### 1. Grill the user

Invoke the `grill-me` skill and follow its workflow and questioning style: restate the request, identify gaps and
decisions, then ask focused questions in small batches until there are no material open questions.

Because this is for a smaller feature, keep the interview proportionate — usually one to three batches. Stop asking once
the goal, scope, inputs/outputs, edge cases, and acceptance criteria are clear enough to slice into tasks. Do not save a
spec file; the plan summary below replaces it.

### 2. Print the plan summary

Print the summary directly in the conversation using this template. Keep it short — this is deliberately less detailed
than a spec. Hard-wrap prose at ~140 columns.

<plan-template>

## Summary

One short paragraph: the problem and the outcome the user wants, from the user's perspective.

## Solution

A short description of the solution from the user's perspective — what will exist or behave differently when this is done.

## Implementation

A brief list of the implementation decisions: modules built or modified, interfaces, schema or API changes, and any
technical clarifications from the user. No file paths or code snippets — they go stale.

## Acceptance

- <Observable condition that proves the work is done. One line each.>

## Out of Scope

- <Explicitly excluded work.>

</plan-template>

### 3. Await approval

Ask: "Happy with this plan, or would you like to adjust anything?"

Wait for explicit approval. If the user asks for changes, revise the summary and ask again. Do not proceed to step 4
without approval.

### 4. Write the tasks

Once approved, invoke the `to-tasks` skill to break the approved plan into vertical-slice tasks and publish them to
`kanban.json`. The approved plan summary is the input — `to-tasks` still runs its own slice proposal, coverage table, and
approval gate before publishing.
