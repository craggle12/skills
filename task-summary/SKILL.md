---
name: task-summary
description: Write a substantive end-of-task implementation summary when the user invokes task-summary or requests this reporting style after coding work.
---

# Task Summary

End implementation work with a self-contained summary explaining what changed
and how the resulting behavior works. Match the detail of a useful handover,
not a terse completion notification.

Use the conversation, final changes, and actual verification results as
evidence. Inspect missing context when needed, but do not rerun checks solely
to produce this summary. This skill controls reporting; it does not authorize
extra implementation, commits, or external actions.

## Content and order

1. Open with the task ID/name and the concrete capability or fix delivered.
   If incomplete, state that clearly.

2. Explain the main changes in labeled bullets, grouped by behavior or
   component. Describe triggers, resulting behavior, relevant API/task names,
   configuration defaults, and interactions where they matter. Avoid a
   file-by-file diff recital.

3. Include material edge cases, failure handling, limitations, and meaningful
   refactors. Mention only details supported by the implementation; do not
   invent guarantees.

4. Summarize validation: behaviors covered, actual test count/results when
   available, and formatter/linter/configuration checks. Distinguish passed,
   failed, and unrun checks. For TDD work, briefly identify the behavior
   observed red before implementation and subsequently green.

5. Report bookkeeping actually completed: task status, progress log,
   documentation updates or scheduled follow-ups, and pre-existing changes
   excluded from the commit when relevant.

6. End with commit hash and exact subject, if committed. Otherwise state
   that changes are uncommitted.

## Style

- Typically use an opening sentence, 4–8 explanatory bullets, a validation
  paragraph, and bookkeeping/commit details. Scale down for small changes
  without omitting meaningful behavior.
- Prefer roughly 200–400 words for a substantial task. User-requested detail
  takes precedence.
- Make each bullet explain a concrete change and its practical effect.
  Do not reduce the response to “implemented, tests passed, committed.”
- Keep names, paths, configuration values, and commit subjects exact.
- Even if caveman mode is active, preserve substance and readable
  explanations; compress filler, not technical content.
- Do not print patches or narrate implementation chronology.
- Do not add empty sections or speculative warnings.
