#!/usr/bin/env python3
"""Gather architecture signals from a codebase and print them as JSON.

Usage: python scan_metrics.py <target-dir> [--max-files N]

Stdlib only. The output is a set of leads for a human or model reviewer to
confirm by reading the code; nothing here is a verdict on its own.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

IGNORED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "vendor",
    "venv", ".venv", "env", ".env", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".tox", ".ruff_cache", "dist", "build", "out", "target",
    ".next", ".nuxt", ".svelte-kit", "coverage", ".idea", ".vscode",
    ".gradle", "Pods", "DerivedData", ".terraform", "site-packages",
}

LANGUAGES = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".mjs": "JavaScript", ".cjs": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".java": "Java",
    ".kt": "Kotlin", ".kts": "Kotlin", ".scala": "Scala", ".rb": "Ruby",
    ".php": "PHP", ".cs": "C#", ".fs": "F#", ".c": "C", ".h": "C/C++ header",
    ".cpp": "C++", ".cc": "C++", ".hpp": "C++", ".swift": "Swift",
    ".m": "Objective-C", ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir",
    ".erl": "Erlang", ".clj": "Clojure", ".hs": "Haskell", ".lua": "Lua",
    ".r": "R", ".jl": "Julia", ".vue": "Vue", ".svelte": "Svelte",
    ".sh": "Shell", ".bash": "Shell", ".sql": "SQL",
}

TEST_PATTERNS = [
    re.compile(p) for p in (
        r"(^|/)tests?/", r"(^|/)__tests__/", r"(^|/)spec/",
        r"(^|/)test_[^/]+$", r"_test\.[a-z]+$", r"\.test\.[a-z]+$",
        r"\.spec\.[a-z]+$", r"Tests?\.[a-z]+$",
    )
]

MARKER_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
URL_RE = re.compile(r"""["'](https?://(?:localhost|127\.0\.0\.1|[\w.-]+\.(?:internal|local|corp))[^"']*)["']""")

SWALLOW_PATTERNS = [
    ("bare except", re.compile(r"^\s*except\s*:\s*(#.*)?$")),
    ("except ... pass", re.compile(r"^\s*except[^:]*:\s*pass\b")),
    ("empty catch", re.compile(r"catch\s*(\([^)]*\))?\s*\{\s*\}")),
    ("ignored Go error", re.compile(r"\b_\s*(,\s*_\s*)?=\s*\w[\w.]*\(.*\)\s*$")),
    ("Rust unwrap", re.compile(r"\.unwrap\(\)")),
]

IMPORT_PATTERNS = {
    "Python": [re.compile(r"^\s*from\s+([\w.]+)\s+import"),
               re.compile(r"^\s*import\s+([\w.]+)")],
    "JavaScript": [re.compile(r"""(?:from|require\()\s*["']([^"']+)["']""")],
    "TypeScript": [re.compile(r"""(?:from|require\()\s*["']([^"']+)["']""")],
    "Go": [re.compile(r'^\s*(?:import\s+)?"([\w./-]+)"')],
    "Java": [re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+);")],
    "Kotlin": [re.compile(r"^\s*import\s+([\w.]+)")],
    "C#": [re.compile(r"^\s*using\s+([\w.]+);")],
    "Ruby": [re.compile(r"""^\s*require(?:_relative)?\s+["']([^"']+)["']""")],
}

TOOLING = {
    "ci": [".github/workflows", ".gitlab-ci.yml", ".circleci", "Jenkinsfile",
           "azure-pipelines.yml", ".travis.yml", "bitbucket-pipelines.yml",
           ".buildkite"],
    "build": ["Makefile", "justfile", "Taskfile.yml", "build.gradle",
              "build.gradle.kts", "pom.xml", "CMakeLists.txt", "Rakefile",
              "noxfile.py", "tox.ini", "Dockerfile", "docker-compose.yml",
              "compose.yaml"],
    "lint": [".eslintrc", ".eslintrc.js", ".eslintrc.json", "eslint.config.js",
             "eslint.config.mjs", ".prettierrc", "biome.json", "ruff.toml",
             ".flake8", ".pylintrc", "mypy.ini", ".golangci.yml",
             ".rubocop.yml", "rustfmt.toml", "clippy.toml", ".editorconfig",
             ".pre-commit-config.yaml"],
    "lockfiles": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml",
                  "bun.lockb", "poetry.lock", "uv.lock", "Pipfile.lock",
                  "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock"],
    "docs": ["README.md", "README.rst", "README", "README.txt",
             "CONTRIBUTING.md", "ARCHITECTURE.md", "docs", "adr", "docs/adr"],
}

DUP_WINDOW = 6          # lines per duplicate-detection window
MAX_FILE_BYTES = 1_000_000
CAP = 25                # max items per list in the output


def is_test(rel):
    return any(p.search(rel) for p in TEST_PATTERNS)


def walk(root, max_files):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in IGNORED_DIRS and not d.startswith(".")
                       or d in (".github", ".circleci", ".buildkite")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in LANGUAGES:
                path = os.path.join(dirpath, name)
                try:
                    if os.path.getsize(path) > MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                files.append(path)
                if len(files) >= max_files:
                    return files, True
    return files, False


def read_lines(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except OSError:
        return []


def normalise(line):
    return re.sub(r"\s+", " ", line.strip())


def trivial(line):
    return (not line or len(line) < 4
            or line in {"{", "}", "};", ")", "});", "]", "end", "else:", "} else {"}
            or line.startswith(("import ", "from ", "#include", "using ", "package ")))


def module_key(lang, name, rel):
    """Collapse an import target to a comparable key."""
    if lang in ("JavaScript", "TypeScript"):
        if name.startswith("."):
            base = os.path.normpath(os.path.join(os.path.dirname(rel), name))
            return base.replace(os.sep, "/")
        return None  # external package; not an internal hotspot
    return name


def scan(root, max_files):
    root = os.path.abspath(root)
    files, truncated = walk(root, max_files)

    lang_lines = Counter()
    sizes = []
    markers = []
    marker_counts = Counter()
    swallowed = []
    urls = []
    fan_in = defaultdict(set)
    windows = defaultdict(list)
    src_files = test_files = 0
    src_lines = test_lines = 0

    for path in files:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        ext = os.path.splitext(path)[1].lower()
        lang = LANGUAGES[ext]
        lines = read_lines(path)
        n = len(lines)
        lang_lines[lang] += n
        testy = is_test(rel)
        if testy:
            test_files += 1
            test_lines += n
        else:
            src_files += 1
            src_lines += n
            sizes.append((n, rel))

        norm = []
        for i, line in enumerate(lines, 1):
            m = MARKER_RE.search(line)
            if m:
                marker_counts[m.group(1)] += 1
                if len(markers) < CAP * 2:
                    markers.append({"file": rel, "line": i, "kind": m.group(1),
                                    "text": line.strip()[:160]})
            if not testy:
                for label, pat in SWALLOW_PATTERNS:
                    if label == "Rust unwrap" and lang != "Rust":
                        continue
                    if label == "ignored Go error" and lang != "Go":
                        continue
                    if pat.search(line):
                        swallowed.append({"file": rel, "line": i, "kind": label,
                                          "text": line.strip()[:160]})
                u = URL_RE.search(line)
                if u:
                    urls.append({"file": rel, "line": i, "url": u.group(1)[:120]})
            for pat in IMPORT_PATTERNS.get(lang, []):
                im = pat.search(line)
                if im:
                    key = module_key(lang, im.group(1), rel)
                    if key:
                        fan_in[key].add(rel)
            nl = normalise(line)
            norm.append((i, nl))

        if not testy:
            content = [(i, l) for i, l in norm if not trivial(l)]
            for k in range(len(content) - DUP_WINDOW + 1):
                chunk = content[k:k + DUP_WINDOW]
                digest = hashlib.sha1("\n".join(l for _, l in chunk).encode()).hexdigest()
                windows[digest].append((rel, chunk[0][0], chunk[-1][0]))

    # Duplicates: keep windows that appear in 2+ places, merge overlapping
    # windows within the same file pair into one block.
    dup_groups = defaultdict(list)
    for digest, locs in windows.items():
        uniq = sorted(set(locs))
        if len(uniq) < 2:
            continue
        sig = tuple(sorted({f for f, _, _ in uniq}))
        dup_groups[sig].append(uniq)
    duplicate_blocks = []
    for sig, groups in dup_groups.items():
        groups.sort(key=lambda g: g[0][1])
        merged = []
        for g in groups:
            if merged and all(
                a[0] == b[0] and b[1] <= a[2] + 1
                for a, b in zip(merged[-1], g)
            ) and len(merged[-1]) == len(g):
                merged[-1] = [(a[0], a[1], max(a[2], b[2])) for a, b in zip(merged[-1], g)]
            else:
                merged.append(list(g))
        for m in merged:
            span = max(e - s + 1 for _, s, e in m)
            duplicate_blocks.append({
                "approx_lines": span,
                "locations": [{"file": f, "lines": f"{s}-{e}"} for f, s, e in m[:6]],
                "occurrences": len(m),
            })
    duplicate_blocks.sort(key=lambda d: (d["approx_lines"] * d["occurrences"]), reverse=True)

    hotspots = sorted(
        ({"module": k, "imported_by": len(v)} for k, v in fan_in.items() if len(v) >= 3),
        key=lambda d: d["imported_by"], reverse=True,
    )

    tooling = {}
    for cat, names in TOOLING.items():
        tooling[cat] = [n for n in names if os.path.exists(os.path.join(root, n))]

    sizes.sort(reverse=True)
    total = src_lines + test_lines
    return {
        "target": root,
        "truncated": truncated,
        "totals": {
            "files_scanned": len(files),
            "source_files": src_files,
            "test_files": test_files,
            "source_lines": src_lines,
            "test_lines": test_lines,
            "lines_of_code": total,
        },
        "languages": [{"language": l, "lines": c} for l, c in lang_lines.most_common()],
        "largest_files": [{"file": f, "lines": n} for n, f in sizes[:CAP // 2]],
        "duplicate_blocks": duplicate_blocks[:CAP],
        "swallowed_errors": swallowed[:CAP * 2],
        "swallowed_error_count": len(swallowed),
        "markers": {"counts": dict(marker_counts), "samples": markers},
        "hardcoded_urls": urls[:CAP],
        "import_fan_in": hotspots[:CAP // 2],
        "tests": {
            "test_to_source_line_ratio": round(test_lines / src_lines, 2) if src_lines else None,
            "test_files": test_files,
        },
        "tooling": tooling,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", default=".")
    ap.add_argument("--max-files", type=int, default=5000)
    args = ap.parse_args()
    if not os.path.isdir(args.target):
        sys.exit(f"Not a directory: {args.target}")
    json.dump(scan(args.target, args.max_files), sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
