---
name: adversarial-review
description: Use when the user wants an independent, adversarial review of a completed implementation produced by another coding agent, checked against a frozen spec on a Git branch. Trigger when the user says adversarial review, review this branch against the spec, independently review the implementation, check the agent's work, verify the implementation matches the spec.
---

# Adversarial Review

Perform an independent, targeted review of a completed implementation produced by another coding agent.

Assume nothing the implementing agent claimed is true. Passing tests do not mean the implementation is correct. A plausible-looking
implementation does not mean the spec was interpreted correctly. Verify everything against the spec and the actual code.

Do NOT modify the code at any point during this review.

## Step 1 — Establish review scope

Before doing anything else, ask the user for:

1. **The local Git branch containing the completed implementation**
2. **The base commit** — the last commit before implementation of this task began

Ask in plain text and wait. Do not begin the review until both are provided.

Once provided, verify both exist locally:

```
git rev-parse --verify <BRANCH>
git rev-parse --verify <BASE_COMMIT>
```

Identify the implementation commits:

```
git log --oneline <BASE_COMMIT>..<BRANCH>
```

Inspect the complete implementation diff:

```
git diff <BASE_COMMIT>..<BRANCH>
```

The entire change between `<BASE_COMMIT>` and the current local tip of `<BRANCH>` is the implementation under review.

Do NOT fetch, pull, switch to a remote branch, or otherwise update the repository. Review the local repository state only.

If the branch or base commit cannot be resolved, or the resulting range is empty, STOP and report the problem rather than reviewing an
incorrect change set.

Read relevant surrounding code where necessary to understand how the changed code interacts with the existing system.

## Step 2 — Read the specification

Read the final/frozen specification for this task. Look in `.claude/specs` in the current repo first; if there is no obvious match, ask
the user which spec applies.

The specification is the source of truth and includes the agreed:

- Requirements
- Expected behaviour
- Implementation/design decisions
- Constraints
- Files expected to change
- Tests expected
- Acceptance criteria

Do NOT read `PROGRESS.md` during this initial review. It contains the implementation agent's implementation-time reasoning and may bias
the independent review.

## Step 3 — Review

Perform three independent checks.

### Specification compliance

Check every requirement and acceptance criterion against the actual implementation.

Verify that every requirement is implemented, behaviour matches the specification, agreed design decisions and constraints were followed,
expected changes are present, unexpected changes are justified, and nothing has silently deviated from the specification.

### Implementation correctness

Inspect the complete diff and relevant surrounding code for:

- Logic errors
- Incorrect assumptions
- Boundary and edge cases
- Error and exception paths
- Incorrect state handling
- Resource handling
- Concurrency/race issues where applicable
- Security problems
- Incorrect API/library assumptions
- Regressions
- Unintended interactions with existing code

Focus on realistic failure modes rather than stylistic concerns.

### Test quality

Inspect and run the relevant tests, linting and type checking where available.

Do not merely check whether tests pass. Determine whether they actually prove the specified behaviour.

Look for missing requirement coverage, missing negative tests, missing boundary cases, tests that mirror implementation mistakes, weak
assertions, excessive mocking, and behaviour that requires integration testing.

## Exclusions

Do NOT report:

- Style preferences
- Naming preferences
- Formatting issues handled by tooling
- Speculative refactoring
- Alternative architectures merely because they are preferred
- General "could be improved" observations

Only report actionable findings affecting correctness, specification compliance, reliability, security or meaningful test coverage.

If you cannot demonstrate a concrete problem, do not report it.

## Findings

For every finding provide:

**Severity:** Critical / High / Medium / Low
**Spec requirement:** Requirement or acceptance criterion affected
**Location:** File and line(s)
**Problem:** What is wrong
**Failure scenario:** Concrete example demonstrating the problem
**Test gap:** Why existing tests do not catch it, if applicable
**Recommended fix:** Minimum change necessary

## Final result

Finish with exactly one of:

**PASS** — No actionable correctness or specification-compliance issues found.

**FAIL** — One or more actionable issues found.

If FAIL, list findings in severity order.

Optional improvements must not cause a FAIL.
