---
name: teach-me-quick
description: Use when the user wants a quick, rough-and-ready lesson on a topic using active recall — teach a small chunk, ask one question, check the answer, move on — finishing after a fixed handful of chunks rather than going on forever. Trigger when the user says quick lesson, teach me X quickly, quick and dirty lesson, active recall, quiz me on X, test me on X, or invokes /teach-me-quick <topic>.
---

# Teach Me Quick

A short, bounded teach-then-recall session on one topic. The user wants to *learn* the thing and lock it in, fast — not sit an exam and not get a textbook.

## Shape of the session

1. **Scope it (no questions unless the topic is genuinely ambiguous).** Pick the 4–5 most important ideas for the topic, ordered so each builds on the last. State the plan in one line, e.g. `Plan: 1) what a mixin is · 2) multiple mixins & order · 3) MRO & super() · 4) mixins with __init__ · 5) when not to use one`. If the user gave a number of chunks or a focus, use that instead.
2. **Run each chunk as a loop:**
   - **Teach** — a few sentences plus one small, concrete example (code if the topic is code). Highlight the 2–3 things to notice. Keep it tight: should fit on one screen.
   - **Ask ONE question** — recall or "predict the output"/"what goes wrong" style, answerable from what was just taught. Never batch questions.
   - **Wait** for the answer.
   - **Mark it** — say plainly whether it's right, partly right or wrong. Correct the misconception directly with the minimal example that shows it. If they're partly right, credit the right part first.
   - If they were wrong or unsure, ask **one** quick follow-up on the same idea with a fresh example. Then move on regardless — don't loop forever on one point.
3. **Finish** after the last chunk with:
   - A recap: one line per chunk, the key takeaway.
   - The 1–2 things they got wrong or wobbled on, restated correctly.
   - Optionally 3 rapid-fire review questions (all at once, short answers) — offer, don't force.
   - Then stop. Offer one line: "Want to go deeper on any of these?"

Show progress in each chunk heading: `## 2/5 — Multiple mixins and order`.

## Rules

- **Teach before testing.** Never open with a quiz. Never ask about something not yet taught.
- **One question at a time.** No walls of questions.
- **Reprint any code a question refers to**, right next to the question, even if it was shown earlier. The user should never have to scroll back.
- **Keep track of what the user has already answered.** If they say they answered something, check before re-asking; don't skip or duplicate.
- **Rough answers are fine.** Accept the idea, not the wording; ignore typos.
- **Bounded.** Default 4–5 chunks. Don't add extra chunks unless the user asks.
- **Brief.** No long preambles, no motivational padding. Plain, direct explanations.
- If the user says "stop", "done", or similar, jump straight to the finish recap.
