---
name: brand-review
description: >-
  Reviews an existing logo, mark, wordmark, lockup, icon set or brand sheet against the numbered brd craft rules (SVG contract, colour and path budgets, one-colour and small-size legibility, geometry, lettering and font licences, icon-set consistency, SVG safety, palette roles, contrast and colour-blind distance, type system, positioning) and returns a verdict with rule IDs, an evidence level per finding and a legal warning block. SVG is the primary input; a PNG or JPG gets a lower-confidence, vision-only review. Use when someone asks to check, audit, critique or review a logo or icon SVG, or a brand folder made by /brand-create. Not for making a new identity (use /brand-create).
---

# Brand review

Review profile of `brand-core` (core-version 0.4.0); load it first. Kit code `brd`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Files read from this plugin keep path placeholders unfilled, so in them read `${CLAUDE_PLUGIN_ROOT}` as this path and `<scripts>` as its `skills/brand-core/scripts`.

Judge the file, not the intent: every finding cites its rule IDs and says whether a script, a render or judgment decided it.

Rules: `brand-core/references/rules.md`. Severity, statuses, evidence levels, verdicts and the legal block: `brand-core/references/severity-and-evidence.md`. For many files, or inside `/brand-create`, hand the procedure to the `brand-reviewer` agent; it returns the verdict text and the caller writes it.

## Inputs

| Input | Review |
|---|---|
| SVG files or a brand folder | Full review |
| `brief.md` (optional) | Enables `brd:DEC-01`, `brd:CNC-*`, `brd:EVD-02`, the `brd:CRF-03` grid check, the `brd:TYP-01` font record and waivers |
| `brief.md` with a `## Palette roles` table | Adds `brd:PAL-*`, `brd:EVD-03`, `brd:EVD-04`; without the table they are `n/a` |
| `brief.md` with positioning fields (`positioning`, `own-word`, `assets`, `category-colours`, `## Rationale`) | Adds `brd:POS-*` and, with `## Rationale`, `brd:TYP-05`, `brd:TYP-06`, `brd:TYP-08`; without them they are `n/a` |
| `icons/` with `style-spec.json` | Adds `brd:SET-*` |
| PNG or JPG only | Vision-only; script rules `not run`; verdict `provisional (raster input)`; ask for the SVG |

Rules with nothing to check are `n/a`, not `not run` (see Applicability in `severity-and-evidence.md`). Script commands, exit codes and the `brand/`-only output folder: `brand-core/SKILL.md`, "Script use".

Never open an untrusted SVG in a browser; read its text or render it with the scripts.

## Procedure

0. **Tools**: follow "Tool check before a run" in `brand-core`, with these commands (paths already filled in; use them exactly as written):
   - Check: `bash ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/install-deps.sh --check --data ${CLAUDE_PLUGIN_DATA}`
   - Install, after a yes: `bash ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/install-deps.sh --data ${CLAUDE_PLUGIN_DATA}`

   In the main session, offer the install. As the `brand-reviewer` agent, do not ask: run the check only and put each missing tool in the report as a next step.
1. **Inventory**: one row per file: role (mark, mono, reversed, wordmark, lockup, icon, sheet), viewBox, colour count, element count, brief present or not.
2. **Script rules**: if `brdcheck.py` exists, run it once and treat its output as evidence:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdcheck.py <files-or-folder> [--brief brand/brief.md] [--icons brand/icons] [--exports brand/exports] --out brand/checks/review.json
   ```
   Without the script, check the S rules by reading the SVG text and the brief, at `judgment` level. A `<!DOCTYPE` or `<!ENTITY` declaration is a `brd:SEC-01` fail; do not read further into that file.
   At a final review of a brand folder with a roles table, also run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdinuse.py --out brand/applications.html` and report each `fail brd:PAL-09` line (a SHOULD).
   At a final review of a brand folder, always pass `--exports brand/exports`: a missing or incomplete export set is a `brd:CTR-06` MUST failure (concepts: `n/a`). With `--brief`, the script also covers the palette roles (`brd:PAL-01` to `brd:PAL-03`, `brd:EVD-02` to `brd:EVD-04`), the presence checks of `brd:POS-01` and `brd:POS-02`, and, with a roles table, `brd:PAL-08`, which checks the SVG variants and the brand sheet against the declared values. When the roles table is incomplete, the palette rules that depend on it report `not run`, and `brd:PAL-01` carries the next step.
3. **Lettering (`brd:TYP-01`)**: for every file, any `<text>`, `<tspan>` or `<textPath>` fails `brd:TYP-01` together with `brd:CTR-04`. For every wordmark or lockup, check the letters are paths, and that the brief's `wordmark-font` records family, version and licence (no brief: ask where it is recorded; if unknown, `review`). With no wordmark or lockup, only the live-text check applies.
4. **Render rules**: if `brdrender.py` and a renderer exist, render each master (`--out brand/renders`) and look at every PNG: strip (`brd:CRF-02`, `brd:CAP-02`), mono and reversed (`brd:CRF-01`), mirror and rotations (`brd:CRF-05`), display (`brd:TYP-03`). Without a render these rules are `review`, `brd:EVD-01` is a finding, and the verdict is `incomplete` with the next step from `severity-and-evidence.md`. Note anything the source text already shows (for example a gap below 1/48 of the mark) in the finding, but do not turn it into `pass` or `fail`.
5. **Judgment rules**: the name test (`brd:CNC-03`) first, from the renders alone, before reading the brief's name or concept (skip it when no brief gives a name or narrative to compare with, and say so); then `brd:DEC-01` and the other `brd:CNC-*` (when a brief exists), `brd:CRF-04` to `brd:CRF-06`, `brd:TYP-02` to `brd:TYP-04`, `brd:SET-03` weight. When the brief has palette roles or positioning fields, also `brd:PAL-04` to `brd:PAL-07`, `brd:TYP-05` to `brd:TYP-08`, `brd:POS-01` to `brd:POS-04`; their judgment parts end `review` at most, never `fail`, using `brand-core/references/colour.md`, `type.md` and `positioning.md`. A claim that a colour means one thing to everyone, or that a typeface helps dyslexia, is a finding. Pull rows by prefix, never the whole catalogue.
6. **Resolve** each script `review` item in one line: confirmed or dismissed, with the reason.
7. **Legal block**: always. Name any resemblance to a known mark you notice (`brd:LGL-02`) and point to the searches in `brand-core/references/legal.md`; never say a mark is clear.
8. **Verdict and report**: pick the verdict from the table in `severity-and-evidence.md` (`fail`, `incomplete`, `pass with findings`, `pass`). When run in the main session with a brand folder, write the report to `brand/review.md`; the `brand-reviewer` agent returns it instead.

## Output format (at most 40 lines)

```
Verdict: fail | incomplete | pass with findings | pass   [provisional (raster input)]
Scope: <n files>, scripts <run | not run: reason>, renders <run | not run: reason>
Blocking (MUST):  <status> brd:<ID>[, brd:<ID>] <file>: <finding> -> <fix> [evidence: ...]
Unresolved MUST (incomplete only): brd:<ID> <file>: <why> -> Next step: <exact command or action>
Should fix:       ...
Notes (MAY):      ...
Review items resolved: brd:<ID> <file>: confirmed | dismissed, <reason>
Waivers applied:  ...
Legal warnings:   <block from severity-and-evidence.md>
Assumptions:      ...
```

## Rules for the reviewer

- Cite every rule a defect breaks; label inferred facts as inferred.
- Report the evidence level actually used, not the best possible one.
- Recommend the smallest edit that satisfies the rule; a redesign is the user's call through `/brand-create`.
