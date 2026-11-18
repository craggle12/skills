---
name: code-explanation
description: Explain a small, specific piece of code (one function, fixture, class or short block that the user pastes or names by file and function or line range) in three parts. First a compact table of the libraries and language ideas it uses, then the full code with detailed comments next to the lines, then one example that shows it being used. Requires a target; if none is given, it stops and asks for one. Not for whole files or general codebase breakdowns. Use when the user pastes or points at code and asks to explain it, break it down, walk through it, or says they don't understand it. Unlike code-walkthrough, which traces recent changes through an execution path, this explains any given code line by line.
---

# Code Explanation

Explain the code in chat so the user understands it without looking anything up elsewhere. This is read-only: don't change code.

## Select the code

This skill is for **small, specific pieces of code**: one function, fixture, class, or a short block. It is not for whole files, modules or a general codebase breakdown.

**A target is required.** The user must give one of:
- pasted code,
- a file plus a function or class name (e.g. `tests/conftest.py authenticated_template_client`),
- a file plus a line range (e.g. `src/foo.py:40-90`).

**If no target is given, stop and ask for one.** Don't guess from the conversation, recent changes or open files, and don't start explaining. Ask in one line, for example:
> Which code should I explain? Paste it, or give a file and function name, or a file and line range.

**If the target is too broad** (a whole file, a directory, "the auth system", or more than about 150 lines), stop and ask the user to narrow it to a specific function or block. You can list the main functions or classes in it to help them pick. For a general breakdown, suggest `code-walkthrough` or an architecture review instead.

Once there's a valid target:
- If the code calls into project code that matters for understanding it (a decorator, a fixture, a patched module), read that code too. Explain what it does as far as this code needs it. Say "likely" or "probably" when you're inferring rather than reading.

## Output layout

Use exactly these three parts, in this order, each under its own `##` heading.

### Part 1: Quick reference

A **compact table** of every library call, standard library function and non-obvious language idea the code uses. The user reads this regularly, so it must stay short.

- Columns: `Thing | What it does | Example`.
- One row per item. "What it does" is one plain sentence, written for a developer. Bold the key distinction (e.g. "until the **test** ends").
- The example is **one line** that shows the effect, not just the call: `getattr(math, 'pi')` is the same as `math.pi`.
- Include the language ideas that the code's trick depends on (e.g. decorators run once when the file loads, the import cache). Put these first.
- Skip things any Python developer knows (`print`, `len`, f-strings, plain `import`) unless the code uses them in an unusual way.
- If one line can't show the effect (e.g. something that is set, then undone), add a short code block of at most about 5 lines **below** the table, and write "see below" in its row.
- No "where it's used" notes here; that belongs in Part 2's comments.
- No broad everyday analogies (house-sitting, kitchens). Analogies only if they're close to programming ("like a try/finally that undoes the change").

### Part 2: The code with comments

The **complete** code, with comments written next to the lines they explain.

- Explain the **why**, not just the what: why this approach, why this order, why this argument exists even if it's unused, what would go wrong without it.
- Group comments above each logical step. Use short end-of-line comments for list or dict entries and return values.
- When there's a central problem/solution, label it plainly (`# THE PROBLEM: ...` / `# THE FIX: ...`).
- Point out lifetimes and timing: when something is created, applied, undone, or still in effect after a block or function ends.
- For each library call, say why it's used *here*, without repeating the Part 1 definition.
- Map each branch of conditional logic to its outcome (e.g. `-> 401`, `-> 403`).
- Don't change the code itself; only add comments.

### Part 3: How it's used

- One short, realistic example that uses the code (a test, a caller, a request). Prefer a real one from the repo; otherwise write a minimal plausible one and say it's illustrative.
- Then a numbered list of 3 to 6 steps tracing what happens when that example runs, tying back to the parts explained in Part 2.

## Style

- Plain language, written for a developer. Short sentences.
- Bold sparingly, only for the distinction that matters.
- Don't add an intro or summary paragraph beyond one line saying what the code is for, if that helps.
- End with no follow-up questions unless something was genuinely unclear.

## Example of Part 1 format

| Thing | What it does | Example |
|---|---|---|
| **Decorator** `@d` | Wraps a function **once, when the file loads**. Swapping `d` later changes nothing. | `@d def f` is the same as `f = d(f)` |
| **`monkeypatch.setattr`** | Replaces an attribute until the **test** ends. | `monkeypatch.setattr(math, 'pi', 3)` |
| **`monkeypatch.context()`** | Same, but only until the **`with` block** ends. | see below |
| **`runpy.run_path`** | Runs a `.py` file fresh (no cache) and returns what it defines as a dict. | `run_path('m.py')['add']` gives a fresh `add` |

**`monkeypatch.context()` vs `setattr`:**
```python
monkeypatch.setattr(math, 'pi', 3)       # pi == 3 until the test ends
with monkeypatch.context() as c:
    c.setattr(math, 'pi', 99)            # pi == 99 here
                                         # pi == 3 again once the block ends
```

## Example of Part 2 comment depth

```python
    # THE PROBLEM: auth.jwt_required_groups in memory is a stub that lets everyone in.
    # THE FIX: run auth.py again from disk with runpy. That gives a brand-new copy of
    # everything in the file, untouched by any patching. We take the real decorator out of it.
    real_decorator = runpy.run_path(auth.__file__)['jwt_required_groups']

    # Changes made with `context` are undone when this block EXITS, not at the end of the test.
    # We only need the real decorator in place while the files load (see below).
    with monkeypatch.context() as context:
```
