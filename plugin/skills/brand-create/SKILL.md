---
name: brand-create
description: >-
  Turns a free-text narrative (a story, mission, README or pitch) into a first-draft brand identity as SVG. Writes a brief, builds a metaphor shortlist, draws three greyscale concepts in parallel, stops at one checkpoint with a recommendation, then makes the kit from the pick: palette, outlined wordmark, lockups, an icon set when asked, and a one-page brand sheet with legal warnings. Use when someone asks for a logo, mark, wordmark, icon set, brand identity, brand kit or favicon for a project or product. Not for reviewing an existing logo (use /brand-review) or for charts and diagrams.
---

# Brand create

Workflow profile of `brand-core` (core-version 0.4.0); load it first. Kit code `brd`.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Files read from this plugin keep path placeholders unfilled, so in them read `${CLAUDE_PLUGIN_ROOT}` as this path and `<scripts>` as its `skills/brand-core/scripts`. Pass the root to every agent you start.

One idea, drawn in black from primitives by three designers in parallel, proven by checks and renders, picked by the user once, then edited, never regenerated, into a kit.

References, loaded at the step that needs them:
- `references/concept-method.md`: narrative to brief, shortlist and the three concepts.
- `references/construction.md`: how to draw a master (the `brand-designer` agent reads it).
- `references/kit-steps.md`: palette, wordmark, lockups, icon set, extras, brand sheet.
- `brand-core/references/positioning.md` (step 1 and the kit), `colour.md` (kit palette step), `type.md` (kit wordmark step).

Run in the main session: it starts the agents, writes `brand/review.md` from the reviewer's returned verdict, and is the only one that talks to the user.

## The live page

Do not make the user open a folder. Resolve the **project root** to an absolute path (the folder the user names, else the current directory) and pass `--root <project root>` to every script and the absolute brand folder to every agent. Then run, in the background:

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdlive.py --root <project root> start`

It serves `brand/index.html` on 127.0.0.1 and opens the browser. The page is the **brand design brief**: it shows the questions, the concepts and the kit as they appear, and after `finish` it is the final brief. Use `brdlive.py ... step <id> active|done|skipped` as each step starts and ends (ids: `brief`, `shortlist`, `concepts`, `review`, `pick`, `kit`, `story`, `export`, `final`) and `refresh` after writing files. A step marked done starts the next pending one on its own, and `start` begins with `brief` in progress, so the page never sits idle; mark a step `skipped` when the scope leaves it out.

The page and the terminal tell the same story. Every progress message you give the user in the terminal (what is starting, what the agents are drawing, what the reviewer is checking), post the same text with `say "<text>"`; the page shows it under "Working on". Every question goes in both places: put it on the page with `ask <id> --text ... --suggest ...` (with `--option` for a choice), which prints the same question for you to repeat in the terminal, then run `wait <id>` in the background. The user may answer in either place: an answer on the page notifies you through `wait` as JSON; an answer in the terminal you record with `answer <id> <value>`, so the page shows it as recorded. Never ask a question in only one of them. If the server cannot start (no browser, no loopback), say so, ask the questions in the terminal with the same suggestions, and carry on: the page is then a snapshot written by `refresh`.

## Scope: alternatives A, B, C

Default is **B**. Offer all three only when the user asks what the options are, or the narrative is thin. A request for an icon set alone runs step 5 of `kit-steps.md` on its own, after a brief.

| Option | Produces |
|---|---|
| A minimal | Mark only, one colour, no ramps, one favicon strip, the export set |
| B restructure (default) | Mark, wordmark, lockups, palette roles with ramps and light and dark values, a type pick from the shortlist, positioning fields, brand sheet, the export set |
| C topology move | B plus dark variants, a colour-blind report on the brand sheet, an icon set, app icon and social assets; or, later, a hosted vector engine for organic shapes (not in v1) |

Record the choice in the brief (`scope`). Every option ends with the export set: an SVG copy and transparent PNGs at every `export_sizes_px` for each top-level brand SVG, a manifest and a zip (`kit-steps.md`, step 8; `brd:CTR-06`).

## Steps

### Step 1: brief
- **Inputs:** the narrative; optionally the repo README or a site the user points to (read only).
- **Do:** print the absolute brand folder path. Run the tool check from `brand-core` ("Tool check before a run"), so a missing renderer or font library is offered for install now, not found at step 4. Use these commands exactly as written (paths already filled in): check `bash ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/install-deps.sh --check --data ${CLAUDE_PLUGIN_DATA}`; install after a yes `bash ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/install-deps.sh --data ${CLAUDE_PLUGIN_DATA}`. The wordmark step (`kit-steps.md` step 2) runs `brdtext.py` with `${CLAUDE_PLUGIN_DATA}/venv/bin/python` when it exists, otherwise `python3`. Fill `${CLAUDE_PLUGIN_ROOT}/templates/brief.md` into `brand/brief.md` per `concept-method.md`. Ask once, as questions on the live page, for the `brd:DEC-01` fields the narrative does not give and, for scope B and C, the `positioning` line and `own-word` (`brd:POS-01`, `brand-core/references/positioning.md`), each with your suggested value. Word the own-word question so it explains itself: say it is the one word the brand should come to own in the audience's mind, that no strong alternative already owns, and give a known example before your suggestion.
- **Output:** `brand/brief.md` with the declaration block. **Gate:** none beyond the questions; do not hold the run for an absent user. **If blocked:** proceed with the suggestions, marked `assumed` in the brief and listed in its `Assumed` line.

### Step 2: metaphor shortlist
- **Do:** write 8 to 12 one-liners into the brief's shortlist, name the category clichés, score each line, and choose three distinct lines for the concepts (`brd:CNC-01`, `brd:CNC-02`).
- **Output:** shortlist and three chosen lines in the brief. **Gate:** none.
- **If blocked:** fewer than 8 lines, or fewer than two literal lines scoring 2 or more on the name test, means the shortlist is too narrow: add lines before choosing. A narrative with no usable essence or tension (a name and nothing else) goes back to step 1: ask once, with your suggested answers, and mark what you assume. Never pick three variations of one idea to reach the number.

### Step 3: three concepts in parallel
- **Do:** start three `brand-designer` agents in one message, one per chosen line, each with the absolute brief path, its line, its folder (`brand/concepts/a`, `b`, `c`) and the project root for `--root`. This is the adapter point for a hosted engine later; v1 always uses the agents.
- **Output:** `concept.svg` and `notes.md` per folder, greyscale, already self-checked. Concept files (steps 3 to 5) are never exported. **If blocked:** a designer that returns MUST failures gets one edit round with the findings; then the concept goes to the checkpoint with its failures shown.

### Step 4: independent review
- **Do:** start one `brand-reviewer` agent on the three concept files. Pass only the three `concept.svg` paths and the project root: not the brand name, the concept lines, the brief path or any `notes.md`, and tell it to read nothing else in `brand/`, so the name test stays blind. It returns verdict text only, including the name test (`brd:CNC-03`: its three guesses per mark with no text beside it); write it to `brand/review.md`. Send MUST failures back to the owning designer as an edit (one round).
- **Output:** a verdict per concept in `brand/review.md`. An `incomplete` verdict (for example no renderer) is shown at the checkpoint with its next step.

### Step 5: checkpoint (hard gate)
- **Do:** run `refresh`, put `ask pick --kind pick --text ... --suggest <letter> --option a --option b --option c` on the page and `recommend <letter> "<reason>"`, then `wait pick` in the background. Show, per concept: the render paths (64 px, 16 px, mono, reversed), the one-sentence concept, the name test result, the verdict and open findings, any resemblance noticed (`brd:LGL-02`). Recommend one, with the reason. List every brief field still `assumed`, so the pick also confirms or corrects them.
- **Gate:** the user picks one on the page or in the terminal (or asks for changes to one). **Never continue without a pick**, even when the user is absent; stop and wait. Changes are edits to the picked file.

### Step 6: kit
- **Do:** copy the pick to `brand/mark.svg`, copy its grid unit to the brief, and work through `kit-steps.md` for the chosen scope, editing the master rather than redrawing it. Export every top-level brand SVG, build the zip and write `applications.html` (kit step 8), then run `brand-reviewer` on the whole folder, with the exports checked, and write its returned verdict to `brand/review.md`.
- **Output:** the brand folder layout from `brand-core`. **If blocked:** a missing script or renderer lowers the evidence level; say so in the brand sheet, never skip the rule.

### Step 7: report
- Run `brdlive.py ... finish`; the page becomes the final brief. Tell the user its address and path. List the absolute path of every file written, including the `brand/exports/` folder and the `<name>-brand-assets.zip` path, the story from the brief (a draft until the user confirms it, `brd:POS-05`), the final verdict with its evidence levels (and, if `incomplete`, the next steps), the legal warning block, and what the user must do next (licence checks, trademark searches).
- **If blocked:** the run stopped at the checkpoint, a file is missing, or the verdict is `fail` or `incomplete`: report what exists and what does not, list each failing or unresolved rule with its next step, and do not call the kit final. Claim a file was looked at only when its render exists in `brand/renders/`; render every master, variant and lockup before the final review.

## Rules for this workflow

- Cite `brd:<ID>` for every finding shown to the user.
- Never show the user an SVG that has not passed the script checks and been looked at as a render, unless the evidence gap is stated beside it.
- Never draw letters by hand (`brd:TYP-04`); a wordmark is outlined from an OFL or Apache font.
- Always deliver the downloadable set (SVG, transparent PNG at every export size, and a zip) with every kit; a kit without it is not final (`brd:CTR-06`).
- With a roles table, also deliver `brand/applications.html`: the kit placed in everyday applications with every colour pair measured (`kit-steps.md` step 8, `brd:PAL-09`).
- Agents return at most 300 words; their files stay in the brand folder.
