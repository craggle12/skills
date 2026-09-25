---
name: draw-it
description: Use when the user wants to visualize an idea, workflow, architecture, or system to help them think it through. Trigger when the user says draw it, draw this out, visualize this, show me a diagram, sketch this out, map this out. Defaults to a Mermaid diagram but picks whatever visualization communicates best. When used while building a spec/PRD, the diagram gets embedded in those docs rather than left only in chat.
---

# Draw It

Turn an idea, process, or system into a visual so the user can see it, not just read about it.

## Workflow

1. Identify the shape of what's being visualized: a process flow, architecture, state machine, sequence of
   interactions, timeline, hierarchy, data model, or decision tree.
2. Pick the diagram type that fits that shape (see guide below). Default to Mermaid. Only switch to a
   non-diagram format when it genuinely communicates better (e.g. a table for a comparison matrix).
3. Render the diagram directly in the chat response as a fenced code block so it displays inline. Don't
   create a separate file for it unless asked, or unless step 4 applies.
4. If this is happening inside a spec/PRD workflow (grill-me, to-prd, to-spec) or the user asks for the
   diagram to be part of the docs, also write it into the relevant markdown file with Edit — see
   "Spec/Doc Integration" below. Chat-only is not enough in that case.
5. Keep it focused: only include the nodes and relationships relevant to the point being made. Cut
   anything that doesn't help the user understand the idea faster.
6. If the request is ambiguous or could be visualized multiple valid ways, pick the most likely fit and
   draw it rather than asking - it's cheap to redraw if it's not quite right.

## Diagram Type Guide

Mermaid (default toolkit for most shapes):

- `flowchart` / `graph` — general process flow, multi-step algorithms with loops/merges
- `sequenceDiagram` — interactions between actors/services over time, request/response flows
- `stateDiagram-v2` — state machines, lifecycle transitions
- `erDiagram` — entity relationships, data models, schemas
- `classDiagram` — object/class structure, type relationships
- `gantt` — timelines, schedules, project plans
- `journey` — user journeys
- `graph` with `subgraph` blocks — system architecture, service boundaries, deployment topology

Non-Mermaid fallback (use when it's genuinely clearer than a diagram):

- **ASCII branching diagram — the default for decision trees** (see "Decision Trees" below). Prefer this
  over Mermaid for these; it's faster to read in a terminal-style chat and doesn't need a renderer.
- **ASCII network diagram grouped by DC/site — the default for network/infrastructure topology** (see
  "Network Diagrams" below).
- Markdown table — comparisons, decision matrices, small enumerations
- ASCII/text layout — UI mockups, spatial or physical layouts
- Nested bullet list — a hierarchy so simple that a diagram would add ceremony, not clarity

## Decision Trees

Default to plain ASCII, not Mermaid, for decision trees and similar branching-logic diagrams. Two shapes
depending on structure:

- **Symmetric branching** (a handful of clean forks, similar depth each side) — draw it as a top-down tree
  with `/`, `|`, `\` connectors:

  ```
                      [Outlook?]
                     /     |      \
                Sunny   Overcast   Rain
                  /         |         \
          [Humidity?]     Play      [Wind?]
            /      \                 /      \
         High    Normal          Strong    Weak
          |         |               |        |
     Don't Play   Play         Don't Play   Play
  ```

- **Asymmetric / wide branching** (early-exit checks, cache-hit style logic where branches merge back
  together) — draw it as a left-to-right box-and-arrow flow:

  ```
                                    Yes
                              +-----------> Return cached value
                              |
  [Cache hit?] ----------------+
                              |
                              | No
                              +----> [Fallback fresh?] ----+ Yes --> Read fallback -----+
                                                            |                            +--> Merge --> Return
                                                            +---- No ----> Recompute -----+
  ```

Switch to a Mermaid `flowchart` instead when the ASCII version would get too wide, too deep, or too tangled
to align cleanly (roughly: more than ~4-5 branch points, or box widths that would push past a normal chat
column and force ugly wrapping). Mermaid handles that complexity without manual alignment breaking down.

## Network Diagrams

Default to plain ASCII, not Mermaid, for network/infrastructure topology (routers, switches, links between
data centers or sites). Group devices into columns by DC/site rather than drawing a flat graph:

- Give each DC/site a header (`DC: <name>`) above its devices, arranged left to right.
- Don't box the DC groups by default — a header plus spacing reads as a group cleanly. Only add a box
  around a DC if it has enough devices that grouping is genuinely ambiguous without one.
- Label devices being decommissioned/replaced with `(to be replaced)` / `[DECOMMISSIONED]`, and new
  devices with `(NEW)`.
- Draw links as `───` between devices in the same row, and `│`/`└──`/`┌──` connectors when a link needs to
  drop to a device below or jump between columns.
- Close with a short "Summary" list: removed links, unchanged links, new devices, new links. This is the
  part people actually scan, so keep it accurate even if the ASCII layout is a rough sketch.

If the request describes a *change* (a device swap, new links, decommissioning), draw two stacked blocks —
`BEFORE` and `AFTER` — using the same column layout in both so they're easy to diff by eye. If it's just
describing current-state topology with no change, draw a single diagram.

Example (before/after, device replacement spanning three DCs):

```
════════════════════════ BEFORE ════════════════════════

  DC: LD5                DC: LD8                  DC: SOV

pe-r-01.ld5.uk ────── pe-r-01.ld8.uk ────── pe-r-01.thn.uk
                              │                DC: THN
                              │
                       pe-r-00.ld8.uk ────── pe-r-00.sov
                       (to be replaced)


════════════════════════ AFTER ═════════════════════════

  DC: LD5                DC: LD8                  DC: SOV

pe-r-01.ld5.uk ──┐                          ┌── pe-r-00.sov
                 │                          │
                 └── pe-r-02.ld8.uk (NEW) ──┘
                          │
                          └────── pe-r-01.ld8.uk ────── pe-r-01.thn.uk
                                                            DC: THN
                    pe-r-00.ld8.uk
                     [DECOMMISSIONED]
```

Switch to Mermaid `graph` with `subgraph` blocks per DC instead when there are more than ~5-6 DCs/sites or
dense many-to-many links that ASCII can't align cleanly without breaking.

## Spec/Doc Integration

When the diagram is produced while building a spec (grill-me), PRD (to-prd), or spec doc (to-spec), the
diagram belongs in the doc, not just the chat transcript. Embed the Mermaid block directly in the relevant
markdown file:

- Prefer placing it under "Solution" or "Implementation Decisions" if the existing template has one that
  fits the diagram's content.
- Otherwise add a "Diagram" subheading near the most relevant section.
- If the doc doesn't exist yet, hold the diagram until the doc is created and add it then, unless the user
  wants it in chat only.

## Style

- Keep node/edge labels short - a few words, not sentences.
- Default to top-down (`TD`) flowcharts; switch to left-right (`LR`) only when the flow genuinely reads
  better sideways (e.g. a pipeline with many parallel short stages).
- Don't add colors, styling classes, or icons unless asked - plain Mermaid renders legibly in both light
  and dark themes and ages better than custom styling.
- Don't pad the diagram with a legend or title unless the diagram is genuinely ambiguous without one.
