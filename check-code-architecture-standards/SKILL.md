---
name: check-code-architecture-standards
description: Review the architecture of a codebase against the principles of "The Pragmatic Programmer" (DRY, orthogonality, reversibility, broken windows, tracer bullets, design by contract, crash early, testability, automation, programming by coincidence) and write the findings to a self-contained HTML report in the reviewed directory. Use this whenever the user asks for an architecture review, code health check, design audit, technical debt assessment, coupling or duplication analysis, or asks how "pragmatic" or maintainable a codebase is, even if they don't mention the book by name.
---

# Pragmatic Architecture Review

Assess a codebase the way Hunt and Thomas would: practically, with evidence, and with an eye on what makes code easy to change. The output is an HTML report saved in the directory being reviewed.

## Why this shape

The book's core claim is that good design is design that is *easy to change* (ETC). Every principle here is a lens on that one question. Keep it in mind when judging severity: a finding matters in proportion to how much it makes future change slower, riskier or more surprising.

The report must be grounded in evidence. A finding without a file path and a reason is "programming by coincidence" applied to reviewing, so avoid it.

## Workflow

### 1. Decide the target directory

Use the directory the user names; otherwise use the current working directory. The report is written there as `pragmatic-architecture-review.html` unless the user asks for a different name. Do not write any other files into the target; put intermediate files in a temp directory.

### 2. Gather hard signals

Run the scanner (stdlib Python only, no installs needed):

```bash
python <skill-dir>/scripts/scan_metrics.py <target-dir> > /tmp/pragmatic_scan.json
```

It reports languages, largest files, duplicated code blocks, swallowed errors, TODO/FIXME/HACK markers, import fan-in hotspots, test-to-source ratio and tooling presence (CI, linters, build scripts, lockfiles). Treat these as **leads, not findings**: every signal you report must be confirmed by reading the code.

### 3. Orient yourself

Before judging anything, understand what the system is for and how it is put together. Read the README, the dependency manifests, the entry points and the top-level directory layout. Identify the main modules or layers and how they talk to each other. Write a two- or three-sentence summary of the architecture; it goes at the top of the report.

### 4. Review through each lens

Read `references/principles.md` now. It lists each principle, what it looks like in code, concrete signals and how to judge severity. Work through every lens, following scanner leads and sampling code yourself. For large codebases, prioritise the core domain, the most-imported modules and the largest files rather than trying to read everything.

For each lens give a rating (`good`, `mixed` or `concern`) and a one-or-two-sentence summary. Record findings with:

- the principle they relate to
- a severity (`high`, `medium`, `low`, `info`) using the guidance in the reference
- a short title and a plain-language description of the problem and why it hinders change
- evidence: file paths with line numbers and a short note each
- a concrete, actionable recommendation (what to change, not just "refactor this")

Aim for roughly 8 to 25 findings. Merge repeated instances of one problem into a single finding with multiple evidence entries rather than listing each separately. Also record genuine strengths; a review that only criticises is less trustworthy and less useful.

### 5. Write the findings JSON

Write a JSON file to a temp location (e.g. `/tmp/pragmatic_findings.json`) in exactly this shape:

```json
{
  "project": {
    "name": "my-service",
    "path": "/abs/path/to/target",
    "summary": "Two or three sentences describing the architecture.",
    "languages": ["Python", "TypeScript"],
    "stats": {"source_files": 142, "lines_of_code": 18234, "test_ratio": 0.31}
  },
  "verdict": "One or two sentences: the overall health and the single most important thing to do next.",
  "principles": [
    {"id": "dry", "rating": "mixed", "summary": "..."}
  ],
  "findings": [
    {
      "principle": "dry",
      "severity": "high",
      "title": "Validation rules duplicated across API and worker",
      "description": "...",
      "evidence": [{"file": "api/validate.py", "lines": "12-48", "note": "..."}],
      "recommendation": "..."
    }
  ],
  "strengths": ["..."],
  "next_steps": ["Ordered, concrete actions, most valuable first."]
}
```

Principle ids are listed in `references/principles.md`. `stats` values may come from the scanner output.

### 6. Render the report

```bash
python <skill-dir>/scripts/render_report.py /tmp/pragmatic_findings.json --out <target-dir>/pragmatic-architecture-review.html
```

The renderer validates the JSON and fails with a clear message if something is malformed; fix the JSON and re-run. It escapes all content, so code snippets and paths are safe to include.

### 7. Report back

Tell the user where the report was saved, the overall verdict, and the top three next steps. Keep it short; the detail lives in the report.

## Judgement guidelines

Be calibrated rather than harsh. Small scripts and prototypes deserve different expectations from long-lived production services; say which you think you are looking at and judge accordingly. Distinguish deliberate trade-offs (often documented in comments or ADRs) from accidents. When unsure whether something is a problem, say so in the description and lower the severity rather than overstating it.
