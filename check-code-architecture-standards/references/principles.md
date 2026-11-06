# Principles reference

Each lens below has an `id` (use it in the findings JSON), what the principle means for architecture, signals to look for, and how to judge severity. Scanner fields that help are noted in brackets.

Contents: etc, dry, orthogonality, reversibility, broken_windows, tracer_bullets, contracts, crash_early, testability, automation, coincidence, plain_text

## Severity scale

- **high**: actively makes common changes slow, risky or bug-prone; likely to cause defects or block the team soon.
- **medium**: a real drag on change in part of the system, or a risk that will grow.
- **low**: minor friction, local untidiness, worth fixing opportunistically.
- **info**: an observation or a deliberate trade-off worth noting, no action required.

---

## etc — Easy to Change

The meta-principle the others serve. Rate it last, as a synthesis.

Look for: how many files a typical feature change touches; whether the code is organised around the domain or around technical accidents; whether there is a clear place for new things to go.

Severity: rarely a finding on its own; use it for systemic issues that don't fit one lens (e.g. "every feature requires edits in seven layers").

## dry — Don't Repeat Yourself

Every piece of *knowledge* has one authoritative representation. This is about knowledge, not just text: two identical-looking functions encoding different business rules are not a violation, and one rule expressed in a SQL constraint, a frontend validator and a backend validator is.

Signals: duplicated blocks [duplicate_blocks]; the same constants, magic numbers, URLs or regexes in several places; schemas defined by hand on both sides of an API; config repeated per environment instead of layered; documentation that restates code and has drifted; copy-pasted test setup.

Severity: high when the duplicated knowledge is business logic, validation or security-relevant and the copies have already diverged; medium when duplicated but still consistent; low for boilerplate.

## orthogonality — Decoupling and cohesion

Independent components: changing one shouldn't ripple into others. Each module should do one well-defined thing.

Signals: modules imported by a large fraction of the codebase [import_fan_in]; god files or classes [largest_files]; circular imports; UI code reaching into the database; business logic mixed with I/O, HTTP or framework code; global mutable state and singletons; "utils" or "helpers" dumping grounds; long parameter lists or train-wreck call chains (`a.b().c().d()`, violating the Law of Demeter).

Severity: high when coupling crosses architectural layers or causes cycles; medium for god modules; low for a messy utils file.

## reversibility — No final decisions

Avoid lock-in to a vendor, framework, database or deployment model where it isn't necessary.

Signals: third-party SDKs called directly throughout the code rather than behind a thin adapter; ORM or vendor-specific queries scattered across business logic; framework types leaking into the domain model; hard-coded cloud provider assumptions; no seams where an alternative could be plugged in.

Severity: high only when a plausible change (swapping a payment provider, database or LLM vendor) would require touching much of the codebase. Don't demand abstraction for things that will never change; that is speculative generality, which the book also warns against.

## broken_windows — Software entropy

Small signs of neglect invite more.

Signals: TODO/FIXME/HACK/XXX markers, especially old or in core code [markers]; commented-out code; disabled or skipped tests; lint suppressions; dead code; inconsistent naming and formatting; outdated or missing README; warnings left in builds.

Severity: usually low or medium individually; raise it when the pattern is widespread, because the cumulative effect is the point of the principle.

## tracer_bullets — End-to-end skeleton

A system should have a thin, working path through all its layers that can be extended incrementally.

Signals: is there a clear entry point and a demonstrable end-to-end flow? Can you run the system locally with one command? Are there half-built layers or speculative frameworks with nothing using them? Integration or end-to-end tests that exercise the whole path?

Severity: medium when components exist that are not wired together or can't be run end to end; info when well done.

## contracts — Design by contract and assertive programming

Be explicit about what code requires and guarantees.

Signals: typed interfaces, type hints, schemas or validation at boundaries (API input, config loading, file parsing); preconditions checked; invariants asserted; or, conversely, loosely typed dicts passed everywhere, `any` types, unvalidated external input, implicit assumptions documented only in someone's head.

Severity: high for unvalidated external input at system boundaries; medium for weak internal interfaces between major modules; low for missing hints on small internal helpers.

## crash_early — Dead programs tell no lies

Fail fast and loudly rather than limping on with corrupted state.

Signals: empty catch blocks, bare `except:`, `except Exception: pass` [swallowed_errors]; errors logged and then ignored; functions returning `None` or default values on failure where callers don't check; missing config silently replaced with defaults; retries that hide permanent failures.

Severity: high when swallowed errors sit around I/O, payments, data writes or security; medium elsewhere; low in throwaway scripts.

## testability — Testing ruthlessly, code that is easy to test

Signals: test-to-source ratio [tests]; whether core logic is testable without network, database or clock (pure functions, dependency injection, seams); tests that only cover trivial code; slow or flaky test suites; no tests on the most-changed or most-imported modules; reliance on mocks so heavy the tests mirror the implementation.

Severity: high when the core domain logic has no tests or can't be tested in isolation; medium for gaps in important modules; low otherwise.

## automation — Ubiquitous automation and power tools

Don't do by hand what a machine can do.

Signals: CI configuration [tooling.ci]; build scripts, Makefile, task runner [tooling.build]; linters and formatters [tooling.lint]; lockfiles for reproducible builds [tooling.lockfiles]; manual release steps described in a README; generated code that is hand-edited; no pre-commit or format checks.

Severity: medium when there is no CI on a shared or production codebase; low for missing conveniences.

## coincidence — Programming by coincidence

Code that works without anyone knowing why.

Signals: sleeps or timeouts used to fix races; order-dependent initialisation; reliance on undocumented library behaviour or exact dict ordering; tests that pass only in a certain order; comments like "don't touch, it works"; mysterious magic values.

Severity: high when it touches concurrency or data integrity; medium otherwise.

## plain_text — Knowledge in plain text, configuration outside code

Signals: configuration, feature flags and environment-specific values in code instead of config files or env vars; secrets or credentials in the repository (flag this as **high** without reproducing the secret value in the report); hard-coded hostnames and URLs [hardcoded_urls]; data stored in opaque formats where plain text would do.

Severity: high for committed secrets; medium for environment-specific values baked into code; low for small conveniences.
