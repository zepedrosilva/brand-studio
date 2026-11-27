---
name: brand-core
description: >-
  Brand-studio internal: the shared core that /brand-create, /brand-review and the brand-designer and brand-reviewer agents load first. Holds the principles, the brd rule catalogue, severity, verdicts and evidence levels, the brief declaration block, thresholds, the brand folder layout, legal notes and the contract of the optional scripts. Use when another brand-studio skill or agent loads it, or when looking up a brd rule ID; a user asking to make or check a logo should get /brand-create or /brand-review instead.
---

# Brand core

Core of `brand-studio` (core-version 0.4.0). Kit code `brd`; outside the catalogue tables, every rule ID is written `brd:<ID>`.

A strong first-draft identity is one idea, drawn in black from simple shapes, proven by checks and renders before anyone sees it, with legal risks named but never decided.

## Principles

1. **Concept before drawing.** One idea, one sentence, chosen from a metaphor shortlist built from the narrative.
2. **Black first.** One colour, 16 px and reversed work before any colour or effect is added.
3. **Primitives first, paths second.** Circles, rects, polygons and arcs on a grid; paths only for merged silhouettes.
4. **Prove, do not trust.** Every SVG passes the script checks, then a render critique, before the user sees it.
5. **Letters are outlines from an OFL font.** No model-drawn letters in v1.
6. **One checkpoint.** Three greyscale concepts and a recommendation; the kit is made only after a pick.
7. **Edit, do not regenerate,** once a direction is picked.
8. **Warn, do not decide.** Copyright, trademark and font licences are surfaced with sources and left to the user.

Sources for each principle: `research/brd-research.md`, section "Candidate principles".

## What this core owns

Load only the file the current step needs.

| Topic | File |
|---|---|
| Rule catalogue (all families) | `references/rules.md` |
| Severity, verdicts, statuses, waivers, evidence levels | `references/severity-and-evidence.md` |
| Brief declaration block (fields and the rules they feed) | `references/declaration.md`; blank form `${CLAUDE_PLUGIN_ROOT}/templates/brief.md` |
| Thresholds (single source for the scripts) | `references/thresholds.md` |
| Legal notes (US-centred, warnings only) | `references/legal.md` |
| Colour: roles, ramps, contrast pairs, colour-blind method, what the evidence supports | `references/colour.md` |
| Type: family count, sizes, wordmark choices, dated OFL shortlist, dyslexia claims | `references/type.md` |
| Positioning: statement, word to own, distinctive assets, tone-to-palette and type rationale | `references/positioning.md` |
| Script contract | `scripts/SPEC.md` |

Pull catalogue rows by prefix, never the whole file:

```bash
grep -E '^\| (CTR|SEC)-' ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/references/rules.md
```

## Rule families

| Prefix | Covers | Detect mostly by |
|---|---|---|
| `brd:DEC` | The brief | judgment |
| `brd:CNC` | Concept method: shortlist, one idea | judgment |
| `brd:CTR` | SVG file contract | script |
| `brd:CAP` | Budgets: colours, feature size, path complexity | script, render |
| `brd:CRF` | Logo craft: one colour, small sizes, geometry, shape traps | render, judgment |
| `brd:TYP` | Lettering, fonts and the type system | script, judgment |
| `brd:SET` | Icon-set consistency | script |
| `brd:SEC` | SVG safety | script |
| `brd:EVD` | Checks run on a render; palette contrast and colour-blind distance | render, script |
| `brd:LGL` | Legal warnings (never pass or fail) | judgment, user-run search |
| `brd:PAL` | Palette: roles, hue count, ramps, rationale, category colours | script, judgment |
| `brd:POS` | Positioning: statement, word to own, rationale lines, distinctive assets | judgment |

## Brand folder

Everything the kit writes goes into one folder: `brand/` at the project root. The scripts refuse any other output folder (exit 2); a custom folder is not supported in 0.1.0. Never write elsewhere.

```
brand/
  brief.md                  declaration block, shortlist, waivers
  concepts/a|b|c/           concept.svg and notes.md per concept (greyscale)
  mark.svg                  master: flat colours, at most the colour budget
  mark-mono.svg             one colour on transparent
  mark-reversed.svg         for dark backgrounds; transparent, no background rect
  mark-reversed-tile.svg    optional preview on a dark background (a tile)
  mark-gradient.svg         optional; only beside the flat master (brd:CTR-05)
  wordmark.svg  wordmark-reversed.svg       outlined lettering
  lockup-horizontal.svg  lockup-horizontal-reversed.svg
  lockup-stacked.svg  lockup-stacked-reversed.svg
  icons/<name>.svg  icons/style-spec.json
  renders/                  PNG output of brdrender
  checks/                   JSON output of brdcheck
  exports/                  the downloadable set (brd:CTR-06), made by brdrender --export
    svg/<stem>.svg            copy of every top-level brand SVG
    png/<stem>-<size>.png     transparent PNG at every export_sizes_px
    manifest.json             one entry per file: svg, png per size, transparent, tile
    <name>-brand-assets.zip   svg/ and png/ bundled
  review.md                 latest review verdict, written by the main session
  brand-sheet.md            one-page brand sheet with the legal block
```

These names satisfy the "predictable file names" part of `brd:CTR-03`. Every `*-reversed.svg` is transparent. Tiles are the only exports that keep a background: stems starting with `app-icon`, `social` or `favicon`, or containing `-tile`. Concept files stay out of `exports/`.

## Optional scripts

`brdcheck.py` (script rules), `brdrender.py` (renders for the render rules), `brdtext.py` (text to outlines) `brdinuse.py` (the kit placed in applications) and `brdlive.py` (the live brief page) live in `${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/`; `scripts/SPEC.md` is their contract. They are helpers, never a gate:

- If a script, or the renderer or font library it needs, is missing, run the same rule by reading the SVG or the brief and record the evidence level as `judgment`.
- A render rule (detect E) without any render cannot pass; its status is `review`, and a MUST left in `review` makes the verdict `incomplete`.
- Treat script output as evidence, then confirm or dismiss each `review` item in one line.

### Tool check before a run

Before the first script of a `/brand-create` or `/brand-review` run, check the optional tools once, with the check command that skill gives. The calling skill holds the commands because only its text has the plugin paths filled in; this file is read as a plain file, so a path placeholder here stays unfilled. `CLAUDE_PLUGIN_DATA` is not set in the shell either: never read it from the environment, and never guess the data folder.

- Exit 0: carry on. Exit 3: something is missing; each `missing` line says what the run loses without it.
- Ask the user once, with install as the suggestion: "Install the missing tools now? Recommended: renders and wordmark outlines stay at `script` and `render` evidence instead of `judgment`." On yes, run the install command the calling skill gives; it prints each command before running it. A line telling the user to run a command themselves (one that needs their password) goes to the user as a `! <command>` suggestion.
- On no, or when the install fails, carry on degraded: name the rules that drop to `judgment` or stay `review`, and record the missing tools in the brief's `tools` line. Do not ask again in the same run.
- The Python packages live in a private venv. Run `brdtext.py` with the venv python the calling skill names when it exists, otherwise `python3`; every other script uses `python3`.

### Script use

Run from the project root, so `brand/` resolves. Each script takes file or folder paths (a folder is searched recursively for `*.svg`), prints at most 40 lines and writes JSON under `brand/` only.

| Script | Command | JSON written |
|---|---|---|
| `brdcheck.py` | `python3 <scripts>/brdcheck.py <svg-or-dir>... [--brief brand/brief.md] [--icons brand/icons] [--grid-unit N] --out brand/checks/check.json` | the `--out` path |
| `brdrender.py` | `python3 <scripts>/brdrender.py <svg> [--sizes 16,32,64] --out brand/renders` | `brand/renders/<stem>-render.json` |
| `brdtext.py` | `<python> <scripts>/brdtext.py --font <ttf-or-otf> --text "<name>" --out brand/wordmark.svg` | `brand/wordmark.json` |
| `brdlive.py` | `python3 <scripts>/brdlive.py --root <project> start\|step\|ask\|wait\|answer\|recommend\|refresh\|finish\|stop\|status` | `brand/index.html` and `brand/live/` (page, state, answers); only `/brand-create` uses it |
| `brdinuse.py` | `python3 <scripts>/brdinuse.py [--brief brand/brief.md] [--out brand/applications.html]` | `brand/applications.html` (`brd:PAL-09`; prints `fail brd:PAL-09` for each pair below its floor) |
| `brdrender.py --export` | `python3 <scripts>/brdrender.py <svg> --export` (one SVG per call; default out `brand/exports`) | `brand/exports/svg/`, `brand/exports/png/`, merged into `brand/exports/manifest.json` |
| `brdcheck.py --exports` | `python3 <scripts>/brdcheck.py brand/ --brief brand/brief.md --exports brand/exports --out brand/checks/check.json` | the `--out` path (`brd:CTR-06`; `brd:PAL-08` per file with `--brief`) |

Exit codes: 0 ran, no unwaived MUST failure; 1 a MUST failed (a file refused under `brd:SEC-01` counts); 2 bad input or an `--out` outside `brand/`; 3 a needed tool is missing (renderer or fontTools), so fall back to judgment (the tool check above should have offered the install already). `<python>` is the venv python from the tool check. Exit 1 is a review result, not a crash. Full contract: `scripts/SPEC.md`.

## Safety

- Scripts never execute SVG content and never fetch external references; an SVG with external references is reported, not rendered.
- Never open an SVG from an unknown source in a browser to "look at it"; render it with the scripts or read its text.
- Legal items are warned about with sources and a recheck date, never decided (`references/legal.md`).
- Everything written stays in the brand folder.

## Engine

LLM-written SVG, checked and rendered locally. An image-capable model is strongly recommended, because the craft rules rely on looking at renders. No hosted generator in v1. The adapter point for one later is the concept step of `/brand-create` (step 3); a hosted engine used there must be declared in the brief (`tools`) and triggers `brd:LGL-03`.

## Technology notes

- Target the SVG 1.1 static subset that resvg, librsvg, browsers and design tools all render. SVG 2 is a Candidate Recommendation (snapshot 2026-10-06; recheck 2027-01-15). Source: brief A20, A21.
- Renderers differ on text and filters; masters avoid both, so one renderer is enough. Source: brief "Technology differences".
- svgo v4.1.0 tightened XML parsing, so malformed SVG that passed before may now throw, and the v4 default preset keeps the viewBox; repair before optimising and record the version (checked 2026-11-18; recheck 2027-03-01). Source: brief A22.
