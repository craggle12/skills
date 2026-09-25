---
name: add-task
description: Use when the user wants to add a task to the kanban.json file in the current repo root. Trigger when the user says add task, create a kanban task, or append a task to kanban.
---

# Add Task

Use this skill to append a well-formed task to the `kanban.json` file in the current repository root. The task must be self-contained enough for a context-free subagent to implement it without prior conversation history.

## Workflow

1. Locate `kanban.json` in the current working directory (repo root). If it does not exist, create it with an empty tasks array: `{ "tasks": [] }`.
2. Read the file and parse the `tasks` array.
3. Determine the next task ID by finding the highest existing `TASK-XX` number and incrementing by 1. Start at `TASK-01` if the array is empty.
4. Use the context the user has provided. If any required field is missing or ambiguous, ask one concise clarifying question before proceeding — do not guess.
5. Construct the task object (see schema below).
6. Append the task to the end of `tasks` array and write the updated JSON back to `kanban.json`.
7. Report the new task ID and a one-line summary of what was added.

## Task Schema

Every task must include exactly these fields.

**Line-wrapping rule:** kanban.json is viewed as raw text/JSON, which does not
auto-wrap. Do NOT embed `\n` escapes inside a string to fake a line break —
in a raw-text view that renders as the literal two characters `\` and `n`,
not an actual newline, so nothing wraps. Instead, any field whose text could
exceed 120 characters (`description`, `acceptance_criteria`, and each `steps`
or `tests` entry) must be written as a JSON array of short line-strings, each
≤80 characters, wrapped at word boundaries — one array element per line, the
way JSON's own pretty-printing puts each element on its own physical line.
`description` and `acceptance_criteria` are always arrays of lines. `steps`
and `tests` are always arrays of entries, and each entry is itself an array
of lines (a single-line entry is just a one-element array). Keep each field
as short as the content allows; wrapping is for content that genuinely needs
the space, not an excuse to write long fields. When reconstituting the full
text (e.g. to display the description as a sentence), join a field's lines
with a single space.

```json
{
  "id": "TASK-XX",
  "category": "short-kebab-category",
  "description": [
    "Concrete, outcome-oriented description. Must be specific enough that",
    "a subagent can decide when the task is done without asking for more",
    "context."
  ],
  "files": [
    "relative/path/to/file.go"
  ],
  "steps": [
    ["Ordered, specific implementation step."],
    ["Each step must be actionable and scoped to a single concern."]
  ],
  "tests": [
    ["Describe each test to write or run, including the focused test command."],
    [
      "Example: Write a config_test.go case asserting devmode=true loads",
      "into s.devMode. Run: go test ./strategies/marketarb/..."
    ]
  ],
  "acceptance_criteria": [
    "A single, unambiguous statement of what done looks like — observable",
    "behavior, passing tests, or verifiable output that proves the task",
    "is complete."
  ],
  "passes": false
}
```

Field rules:

- `id`: sequential, zero-padded, e.g. `TASK-01`, `TASK-02`. Never reuse an existing id.
- `category`: lowercase kebab-case, short (1–3 words). Examples: `config`, `strategy-state`, `dev-mode`, `tests`, `docs`.
- `description`: array of ≤80-char lines (see line-wrapping rule) that join into an outcome-oriented description. State what the code will do when done, not the steps to get there. Include key constraints, environment variables, or behavioral conditions relevant to the feature.
- `files`: every repo-relative file the task is expected to touch. Include new files at their planned path. Never use wildcards.
- `steps`: array of entries, one per implementation step, each entry itself an array of ≤80-char lines. Steps must be ordered and complete enough for a context-free agent. Include behavior, constraints, and edge cases. Do not include test commands here — those belong in `tests`.
- `tests`: array of entries, one per test or test command, each entry itself an array of ≤80-char lines. Include: any red test to write first, what it asserts, and the exact focused test command to run (e.g. `go test ./path/...`). Do not omit the test command.
- `acceptance_criteria`: array of ≤80-char lines that join into one or two falsifiable sentences. Example: "All tests in `go test ./strategies/marketarb/...` pass, and a smoke run with `DEVMODE=true` logs size-capped orders and position-guard skips with no panics."
- `passes`: always `false` when adding a new task. Only a later agent pass changes this to `true` after verification.

## Writing Quality Rules

- The task must be independent: a subagent with no conversation history must be able to pick it up and implement it.
- Do not duplicate context that is already in `CLAUDE.md` — reference it by name if needed.
- Keep `steps` ordered and atomic. Each step should be doable and verifiable on its own.
- Do not invent file paths — only list files the user has identified or that clearly exist in the repo.
- Keep the JSON valid: no comments, no trailing commas, double-quoted strings only.

## Completion

After writing the file, output:

```
Added TASK-XX to kanban.json — <one-line description of what the task implements>.
```
