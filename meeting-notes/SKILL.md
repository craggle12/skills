---
name: meeting-notes
description: Use when the user wants to capture rough/shorthand meeting notes over the course of a conversation and later have them cleaned up into a structured meeting notes document. Trigger when the user says start meeting notes, take meeting notes, or later says summarize/summarise (in the context of notes already given).
---

# Meeting Notes

Use this skill to capture rough, shorthand, or fragmentary notes dropped in over one or more messages, then produce a clean structured meeting notes document on request.

## Workflow

1. **Start.** When the skill is invoked, acknowledge that you're in notes-capture mode. Accept raw notes as given — fragments, abbreviations, bullet dumps, whatever form they arrive in. Do not clean up or restructure yet.
2. **Collect.** As the user pastes more notes or adds corrections/clarifications across the conversation, just absorb them. Ask a clarifying question only if something is ambiguous enough that guessing wrong would materially change the document (e.g. a likely typo in a site/system name) — otherwise hold off and note it for the summary step.
3. **Wait for the summarize trigger.** Do not produce the structured document until the user asks you to summarize/summarise (or clearly signals the notes are complete).
4. **Summarize.** When triggered, turn all notes gathered so far in the conversation into a clean Markdown meeting notes document:
   - Organize into logical sections (e.g. Scope, Networking, Action Items, Open Questions) based on the actual content — don't force a fixed template onto notes that don't fit it.
   - Convert loose asides into an **Action Items** table (Owner | Action) when the notes imply follow-ups.
   - Flag anything ambiguous, contradictory, or a likely typo as an explicit callout rather than silently guessing.
   - Keep the tone concise and factual — this is a record, not prose.
5. **Save.** Write the document to the session scratchpad directory (the path given in the environment's "Scratchpad Directory" section) as a file named:
   `meeting-notes-YYYY-MM-DD.md`
   using today's date. If a meeting notes file for the same date already exists in that location from earlier in the session, overwrite it (it's the same working doc, now more complete) rather than creating a duplicate.
6. **Report.** Reply with the saved file path and remind the user this is a temporary location — offer to move/export it (e.g. as a Google Doc, or into a project directory) if they want it kept longer-term.

## Notes

- This skill only produces the write-up on request — don't summarize mid-stream just because a pause occurred.
- If the user gives corrections after a summary was already produced (like renaming a site or adding a detail), fold them into the existing saved file rather than starting a new document, and reprint the updated section.
