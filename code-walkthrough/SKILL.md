---
name: code-walkthrough
description: Explain recent code changes or a specified Git commit by tracing one real request or event through success and failure, with file/function references and precise test evidence. Use when the user wants to understand completed work through an execution walkthrough.
---

# Code Walkthrough

Explain completed work in chat through a concrete execution path. This is a read-only review; do not change code or write tests unless requested.

## Select the work

Accept an optional commit SHA, Git ref, or range. Inspect a single commit against its first parent (empty tree for a root commit), or the supplied range. Exclude unrelated working-tree edits.

Without an argument, use the most recently completed work from the conversation, checking Git status, diffs, and recent history. Include related uncommitted work. Without useful conversation context, prefer uncommitted runtime changes; otherwise use the latest implementation commit. If HEAD only changes documentation or bookkeeping, inspect preceding history to identify the implementation it describes. State the selected scope and any inference. Ask only when competing scopes materially change the explanation and available evidence cannot resolve them.

For a historical commit, inspect source and tests at that revision without switching branches or disturbing the worktree. Identify the revision and distinguish historical references from current-file links if contents differ.

## Trace the behavior

Read the patch and relevant tests. Pick one real request or event that exercises the change, preferably from an API or integration test added with the work. Name the test, concrete inputs, and setup. If no suitable test exists, say so and choose a scenario supported by code. Do not claim authorship of tests merely because they exist.

Follow the existing entry point through important decisions, state changes, side effects, and the observable final outcome. At each important step, give a file/line link and function name; explain what runs, what decision it makes, what state it changes, and where control goes next. Explicitly identify where new code connects to the existing flow. Avoid exhaustive call graphs and line-by-line narration.

Cross asynchronous boundaries explicitly: identify message contents, what the worker reloads, and when the API returns relative to task completion.

Trace one realistic failure through the same flow, preferably a tested one. Explain whether it raises, retries, records an error, or returns normally. Distinguish HTTP response, task execution status, and domain outcome. Describe actual responses, persisted results, job status, or logs without inventing logging, retry behavior, endpoints, or error details. Identify the first useful debugging location and the concrete inputs, records, or identifiers to inspect.

Separate exactly what tests assert from behavior verified only by reading code. Do not attribute detailed payload checks to a test that checks only an outcome. Distinguish test definitions from tests actually executed in this review, and local task execution from a real broker and separate worker. Mention material harness limitations, including mocked authentication.

Run a focused existing test only when useful and safe under repository instructions. A test run is not required to explain code. State when tests were not rerun; label prior recorded results as prior results. If tracing reveals a concrete defect, explain the evidence and consequence without expanding into an unsolicited audit or fix.

## Required output shape

Use the format below consistently, scaling detail to the change:

1. Open with the selected scope and commit(s), if applicable, and the chosen request/event and test.
2. Include a compact ASCII diagram in a plain-text code block before the numbered walkthrough. Show the entry point, major functions, decisions, persistence, asynchronous handoffs, and observable outcome. Mark the new connection and the chosen failure branch. Distinguish the API response from later worker completion. Use actual function names and keep it readable without horizontal scrolling; omit incidental calls.
3. Give a numbered success walkthrough. Each step starts with **a concrete role and function name**, then a file/line link. Explain execution, decisions, state changes, and the next handoff in connected prose. Call out the new connection to existing code. End at the observable outcome.
4. Trace the failure in a few paragraphs, including visible response/status/logging and where to start debugging. Include a small exact payload only when source supports it.
5. List exactly what the relevant tests assert. Follow with what was verified only by reading code, whether tests ran, and material harness limitations.
6. Finish with the two or three functions the user should read themselves, linked, with a brief reason for each.

Use exact function names, outcome values, and important configuration names. Prefer absolute clickable local file links with line numbers matching the inspected revision. Do not add a repetitive concluding summary.

## Invocation examples

- `$code-walkthrough` — explain the most recently completed work.
- `$code-walkthrough 6ae0332` — explain that commit.
- `$code-walkthrough main..HEAD` — explain that range through one representative flow.
