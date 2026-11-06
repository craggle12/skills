#!/usr/bin/env python3
"""Render pragmatic architecture review findings (JSON) to a self-contained HTML page.

Usage: python render_report.py findings.json --out path/to/report.html
"""

import argparse
import datetime as dt
import json
import sys
from html import escape

PRINCIPLES = {
    "etc": ("Easy to Change", "The meta-principle: good design is design that is easy to change."),
    "dry": ("DRY", "Every piece of knowledge has a single, authoritative representation."),
    "orthogonality": ("Orthogonality", "Independent, cohesive components; changes don’t ripple."),
    "reversibility": ("Reversibility", "No final decisions; avoid unnecessary lock-in."),
    "broken_windows": ("Broken Windows", "Small signs of neglect invite more decay."),
    "tracer_bullets": ("Tracer Bullets", "A thin, working end-to-end path you can build on."),
    "contracts": ("Design by Contract", "Explicit requirements and guarantees at boundaries."),
    "crash_early": ("Crash Early", "Dead programs tell no lies; fail fast and loudly."),
    "testability": ("Testability", "Test ruthlessly; write code that is easy to test."),
    "automation": ("Automation", "Don’t do by hand what a machine can do."),
    "coincidence": ("No Coincidences", "Know why your code works."),
    "plain_text": ("Plain Text & Config", "Keep knowledge and configuration out of code."),
}
SEVERITIES = ["high", "medium", "low", "info"]
RATINGS = {"good", "mixed", "concern"}


def fail(msg):
    sys.exit(f"render_report: {msg}")


def validate(data):
    if not isinstance(data, dict):
        fail("top level must be an object")
    for key in ("project", "principles", "findings"):
        if key not in data:
            fail(f"missing required key '{key}'")
    if not data["project"].get("name"):
        fail("project.name is required")
    for i, p in enumerate(data["principles"]):
        if p.get("id") not in PRINCIPLES:
            fail(f"principles[{i}].id '{p.get('id')}' is not one of {sorted(PRINCIPLES)}")
        if p.get("rating") not in RATINGS:
            fail(f"principles[{i}].rating must be one of {sorted(RATINGS)}")
    for i, f in enumerate(data["findings"]):
        if f.get("principle") not in PRINCIPLES:
            fail(f"findings[{i}].principle '{f.get('principle')}' is not a known principle id")
        if f.get("severity") not in SEVERITIES:
            fail(f"findings[{i}].severity must be one of {SEVERITIES}")
        for k in ("title", "description", "recommendation"):
            if not f.get(k):
                fail(f"findings[{i}].{k} is required")
        if not isinstance(f.get("evidence", []), list):
            fail(f"findings[{i}].evidence must be a list")


def e(x):
    return escape(str(x if x is not None else ""))


def stat_tiles(project, findings):
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITIES}
    tiles = [(counts["high"], "High"), (counts["medium"], "Medium"),
             (counts["low"], "Low"), (counts["info"], "Info")]
    stats = project.get("stats") or {}
    if "source_files" in stats:
        tiles.append((f"{stats['source_files']:,}" if isinstance(stats['source_files'], int) else stats['source_files'], "Source files"))
    if "lines_of_code" in stats:
        tiles.append((f"{stats['lines_of_code']:,}" if isinstance(stats['lines_of_code'], int) else stats['lines_of_code'], "Lines of code"))
    if stats.get("test_ratio") is not None:
        tiles.append((stats["test_ratio"], "Test : source"))
    out = []
    for i, (v, label) in enumerate(tiles):
        cls = f" sev-{SEVERITIES[i]}" if i < 4 else ""
        out.append(f'<div class="tile{cls}"><div class="tile-v">{e(v)}</div><div class="tile-l">{e(label)}</div></div>')
    return "".join(out)


def principle_cards(principles, findings):
    by_id = {p["id"]: p for p in principles}
    cards = []
    for pid, (name, blurb) in PRINCIPLES.items():
        p = by_id.get(pid)
        if not p:
            continue
        n = sum(1 for f in findings if f["principle"] == pid)
        cards.append(
            f'<button class="pcard rating-{e(p["rating"])}" data-principle="{e(pid)}" aria-pressed="false">'
            f'<div class="pcard-top"><span class="pname">{e(name)}</span>'
            f'<span class="badge r-{e(p["rating"])}">{e(p["rating"])}</span></div>'
            f'<div class="pblurb">{e(blurb)}</div>'
            f'<div class="psum">{e(p.get("summary", ""))}</div>'
            f'<div class="pcount">{n} finding{"s" if n != 1 else ""}</div></button>'
        )
    return "".join(cards)


def finding_html(f, idx):
    name = PRINCIPLES[f["principle"]][0]
    ev = []
    for item in f.get("evidence", []):
        loc = e(item.get("file", ""))
        if item.get("lines"):
            loc += f':{e(item["lines"])}'
        note = f' <span class="evnote">— {e(item["note"])}</span>' if item.get("note") else ""
        ev.append(f"<li><code>{loc}</code>{note}</li>")
    ev_html = f'<div class="label">Evidence</div><ul class="evidence">{"".join(ev)}</ul>' if ev else ""
    return (
        f'<article class="finding" data-severity="{e(f["severity"])}" data-principle="{e(f["principle"])}" id="f{idx}">'
        f'<header><span class="sev sev-{e(f["severity"])}">{e(f["severity"])}</span>'
        f'<span class="ptag">{e(name)}</span></header>'
        f'<h3>{e(f["title"])}</h3>'
        f'<p>{e(f["description"])}</p>'
        f'{ev_html}'
        f'<div class="rec"><div class="label">Recommendation</div><p>{e(f["recommendation"])}</p></div>'
        f'</article>'
    )


def list_section(title, items, ordered=False):
    if not items:
        return ""
    tag = "ol" if ordered else "ul"
    lis = "".join(f"<li>{e(i)}</li>" for i in items)
    return f'<section class="card"><h2>{e(title)}</h2><{tag} class="plain">{lis}</{tag}></section>'


CSS = """
:root{color-scheme:light;--bg:#f6f5f1;--surface:#fff;--surface2:#f0eee8;--text:#1d1c1a;--muted:#6b6862;
--border:#e2dfd7;--accent:#2f5d50;--high:#b3261e;--high-bg:#fbe9e7;--med:#a85d00;--med-bg:#fdf0dc;
--low:#2e6a9e;--low-bg:#e5f0fa;--info:#5f5b55;--info-bg:#eeece7;--good:#2e7d4f;--good-bg:#e3f3e8;
--mixed:#a85d00;--mixed-bg:#fdf0dc;--concern:#b3261e;--concern-bg:#fbe9e7;
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--bg:#151514;--surface:#1f1e1c;
--surface2:#2a2926;--text:#ecebe7;--muted:#a19d95;--border:#363430;--accent:#7cc4ad;--high:#ff8a80;--high-bg:#3b1d1a;
--med:#ffb44d;--med-bg:#3a2a12;--low:#8cc4f5;--low-bg:#172a3b;--info:#bdb8b0;--info-bg:#2a2926;--good:#7fd19e;
--good-bg:#173323;--mixed:#ffb44d;--mixed-bg:#3a2a12;--concern:#ff8a80;--concern-bg:#3b1d1a}}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:2rem 1.25rem 4rem}
h1{font-size:clamp(1.6rem,4vw,2.3rem);margin:.2rem 0 .4rem;letter-spacing:-.01em}
h2{font-size:1.15rem;margin:0 0 .8rem}
h3{font-size:1.05rem;margin:.5rem 0 .4rem}
.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:.75rem;color:var(--accent);font-weight:600}
.meta{color:var(--muted);font-size:.9rem}
.summary{max-width:70ch}
.verdict{border-left:4px solid var(--accent);background:var(--surface);padding:1rem 1.2rem;border-radius:8px;margin:1.2rem 0;font-size:1.05rem}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:.75rem;margin:1.2rem 0 2rem}
.tile{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.8rem 1rem}
.tile-v{font-size:1.6rem;font-weight:700}.tile-l{color:var(--muted);font-size:.85rem}
.tile.sev-high .tile-v{color:var(--high)}.tile.sev-medium .tile-v{color:var(--med)}
.tile.sev-low .tile-v{color:var(--low)}.tile.sev-info .tile-v{color:var(--info)}
.pgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:.75rem;margin-bottom:2rem}
.pcard{all:unset;cursor:pointer;display:block;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:.9rem 1rem;border-top:4px solid var(--border)}
.pcard.rating-good{border-top-color:var(--good)}.pcard.rating-mixed{border-top-color:var(--mixed)}.pcard.rating-concern{border-top-color:var(--concern)}
.pcard:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.pcard[aria-pressed="true"]{box-shadow:0 0 0 2px var(--accent)}
.pcard-top{display:flex;justify-content:space-between;align-items:center;gap:.5rem}
.pname{font-weight:650}.pblurb{color:var(--muted);font-size:.82rem;margin:.25rem 0 .5rem}
.psum{font-size:.9rem}.pcount{color:var(--muted);font-size:.8rem;margin-top:.5rem}
.badge,.sev,.ptag{display:inline-block;font-size:.72rem;font-weight:650;text-transform:uppercase;letter-spacing:.05em;padding:.15rem .5rem;border-radius:999px}
.r-good{background:var(--good-bg);color:var(--good)}.r-mixed{background:var(--mixed-bg);color:var(--mixed)}.r-concern{background:var(--concern-bg);color:var(--concern)}
.sev-high.sev{background:var(--high-bg);color:var(--high)}.sev-medium.sev{background:var(--med-bg);color:var(--med)}
.sev-low.sev{background:var(--low-bg);color:var(--low)}.sev-info.sev{background:var(--info-bg);color:var(--info)}
.ptag{background:var(--surface2);color:var(--muted);margin-left:.4rem}
.filters{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:0 0 1rem}
.filters button{font:inherit;font-size:.85rem;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:999px;padding:.3rem .8rem;cursor:pointer}
.filters button[aria-pressed="true"]{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.finding{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;margin-bottom:.8rem}
.finding p{margin:.3rem 0 .6rem}
.label{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:600;margin-top:.6rem}
.evidence{margin:.3rem 0;padding-left:1.1rem;overflow-x:auto}
.evidence code,code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.85rem;background:var(--surface2);padding:.05rem .35rem;border-radius:4px;word-break:break-all}
.evnote{color:var(--muted);font-size:.9rem}
.rec{background:var(--surface2);border-radius:8px;padding:.4rem .9rem .2rem;margin-top:.6rem}
.rec .label{margin-top:.3rem}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:1.1rem 1.3rem;margin-top:1.2rem}
.plain{margin:0;padding-left:1.2rem}.plain li{margin:.3rem 0}
.empty{color:var(--muted);font-style:italic;display:none}
footer{color:var(--muted);font-size:.8rem;margin-top:2.5rem}
@media print{.filters{display:none}.finding{break-inside:avoid}}
"""

JS = """
(function(){
  var sev=null, pr=null;
  var items=[].slice.call(document.querySelectorAll('.finding'));
  var empty=document.getElementById('empty');
  function apply(){
    var shown=0;
    items.forEach(function(el){
      var ok=(!sev||el.dataset.severity===sev)&&(!pr||el.dataset.principle===pr);
      el.style.display=ok?'':'none'; if(ok) shown++;
    });
    empty.style.display=shown?'none':'block';
    document.querySelectorAll('.filters button').forEach(function(b){
      b.setAttribute('aria-pressed', String((b.dataset.sev||null)===sev));
    });
    document.querySelectorAll('.pcard').forEach(function(c){
      c.setAttribute('aria-pressed', String(c.dataset.principle===pr));
    });
    var lbl=document.getElementById('plabel');
    lbl.textContent = pr ? ('Showing: ' + document.querySelector('.pcard[data-principle="'+pr+'"] .pname').textContent + ' — click the card again to clear') : '';
  }
  document.querySelectorAll('.filters button').forEach(function(b){
    b.addEventListener('click',function(){ sev=b.dataset.sev||null; apply(); });
  });
  document.querySelectorAll('.pcard').forEach(function(c){
    c.addEventListener('click',function(){
      pr = (pr===c.dataset.principle)?null:c.dataset.principle; apply();
      document.getElementById('findings').scrollIntoView({behavior:'smooth'});
    });
  });
  apply();
})();
"""


def render(data):
    project = data["project"]
    findings = sorted(data["findings"], key=lambda f: SEVERITIES.index(f["severity"]))
    now = dt.datetime.now().strftime("%d %B %Y, %H:%M")
    langs = ", ".join(project.get("languages") or [])
    meta_bits = [e(project.get("path", ""))] if project.get("path") else []
    if langs:
        meta_bits.append(e(langs))
    meta_bits.append(f"Generated {e(now)}")
    verdict = f'<div class="verdict">{e(data["verdict"])}</div>' if data.get("verdict") else ""
    filter_btns = '<button data-sev="">All</button>' + "".join(
        f'<button data-sev="{s}">{s.capitalize()}</button>' for s in SEVERITIES)
    body = "".join(finding_html(f, i) for i, f in enumerate(findings))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Pragmatic Architecture Review — {e(project["name"])}</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">Pragmatic Architecture Review</div>
  <h1>{e(project["name"])}</h1>
  <div class="meta">{" · ".join(meta_bits)}</div>
  {f'<p class="summary">{e(project["summary"])}</p>' if project.get("summary") else ""}
  {verdict}
  <div class="tiles">{stat_tiles(project, findings)}</div>

  <h2>Principles</h2>
  <div class="pgrid">{principle_cards(data["principles"], findings)}</div>

  <h2 id="findings">Findings</h2>
  <div class="filters">{filter_btns}<span class="meta" id="plabel"></span></div>
  {body}
  <p class="empty" id="empty">No findings match this filter.</p>

  {list_section("Strengths", data.get("strengths"))}
  {list_section("Recommended next steps", data.get("next_steps"), ordered=True)}

  <footer>Lenses drawn from <em>The Pragmatic Programmer</em> by Andrew Hunt and David Thomas. Findings are a reviewer’s judgement based on sampled code; verify before acting.</footer>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("findings")
    ap.add_argument("--out", default="pragmatic-architecture-review.html")
    args = ap.parse_args()
    try:
        with open(args.findings, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {args.findings}: {exc}")
    except OSError as exc:
        fail(str(exc))
    validate(data)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render(data))
    print(f"Wrote {args.out} ({len(data['findings'])} findings)")


if __name__ == "__main__":
    main()
