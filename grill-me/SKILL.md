---
name: grill-me
description: Use when the user wants to turn rough requirements, an idea, a feature request, or an implementation plan into an agreed Markdown spec through direct questioning before coding or execution. Trigger when the user says grill me, create a spec, question my requirements, help refine requirements
---

# Grill Me

Use this skill to convert initial requirements into a concrete, agreed spec. The core behavior is to question the user until the objective, constraints, scope, and acceptance criteria are clear enough to implement or delegate.

## Workflow

1. Restate the initial request in one short paragraph.
2. Identify gaps, risks, and decisions that would affect implementation.
3. Ask focused questions in small batches.
4. Incorporate the user's answers into a working spec.
5. Repeat until there are no material open questions.
6. Save the agreed spec as Markdown if requested. We normally make a spec using /to-spec skill

Do not start implementation work while using this skill unless the user explicitly exits the spec process and asks to implement.

## Questioning Style

Be direct and specific. Prefer questions that force useful decisions over broad prompts.

Ask about:

- Goal: the outcome the user wants.
- Users: who or what will use the result.
- Scope: what is included and excluded.
- Inputs and outputs: files, commands, APIs, formats, schemas, or UI surfaces.
- Constraints: chunking rules, security, performance, compatibility, dependencies, deadlines.
- Edge cases: failure modes, empty states, retries, idempotency, stale data, concurrency.
- Validation: tests, manual checks, metrics, or acceptance criteria.
- Rollout: whether work should be staged, behind flags, mocked first, or split by epics.

Keep each question batch short. Ask one to five questions depending on complexity. If the user gives a strong preference, treat it as a decision and move on.

## Spec Location

Will be converted to Spec

## Out Of Scope

- <Explicitly excluded work.>

## Open Questions

- <Remaining question, or "None".>

## Acceptance Criteria

- <Observable condition that proves the spec is satisfied.>

## Implementation Notes

- <Optional technical guidance, chunking plan, or file/module boundaries.>
```

## Completion Rule

Before saving, summarize the conversation and ask for confirmation that it is agreed. 
