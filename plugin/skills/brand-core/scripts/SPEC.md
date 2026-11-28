# Script specification

Contract for three optional helpers (built and tested; see tests/), Python 3 standard library for everything they do themselves. Each reads its numbers from `../references/thresholds.md` (the YAML block) and never hard-codes them. Each ships fixtures and a regression test under `skills/brand-core/tests/` (repo rule: a skill that ships scripts ships `tests/*.test.sh`).

## Shared behaviour

- **Safety.** Never execute or evaluate SVG content; parse it as data only. A file with a `<!DOCTYPE` or `<!ENTITY` declaration is not parsed: it is a `brd:SEC-01` `fail` (entity-expansion risk), and the script moves on to the next file. Never fetch a URL or follow an external `href`. Write only under `--out`, which must resolve inside `./brand/` relative to the current directory (the brand folder is fixed in 0.1.0; a custom folder exits 2); refuse other paths (exit 2).
- **`--root DIR`.** All three scripts take it: the script changes to `DIR` before anything else, so `brand/` and every relative path resolve against it, not against the caller's folder (an agent often starts in another checkout). A `DIR` that is not a directory exits 2 with a message.
- **Waivers.** Read `brief.md` `## Waivers` lines (`Waives brd:<ID> for <file>: ... Review by: <date>.`); an exact match on rule and file (full path, base name or path suffix) turns `fail` into `waived`, unless the review date has passed.
- **Output.** A JSON file (`--out`) and a compact text summary on stdout of at most 40 lines (36 finding lines, then "... N more in <out>"): one finding line per defect in the format of `../references/severity-and-evidence.md`, with `evidence: script` or `evidence: render`. A defect that breaks several rules lists all of them on one line (brdcheck merges findings with the same status, file and text).
- **Statuses.** `pass | fail | review | waived | not run | n/a` (`n/a`: the rule has nothing to check, for example a brief with no palette yet).
- **Optional-dependency detection.** Scripts with optional dependencies (brdrender, brdtext) detect what is installed (`shutil.which` for binaries, `importlib.util.find_spec` for modules) and record what they used in the JSON under `tools`. brdcheck has none, so its `tools` is `{}`. A missing optional dependency never raises a stack trace: the script exits 3 with an install hint, and the skill falls back to judgment. `install-deps.sh` (bash, not Python) checks for these tools up front and, after the user agrees, installs them: the renderer through the system package manager, `fontTools` and `uharfbuzz` (pinned) in a venv under `--data` (the skills pass `${CLAUDE_PLUGIN_DATA}`). `--check` installs nothing and exits 3 when a tool is missing; a bad argument, or an install without `--data`, exits 2. Decision: `docs/decisions/0009`.

### JSON shape

```json
{
  "script": "brdcheck", "version": "0.1.0", "thresholds": "references/thresholds.md",
  "tools": {"resvg": "0.x", "rsvg-convert": null, "fontTools": null, "uharfbuzz": null},
  "files": ["brand/mark.svg"],
  "rules_checked": ["CTR-01", "CAP-01"],
  "findings": [
    {"id": "brd:CAP-01", "severity": "SHOULD", "status": "fail", "file": "brand/mark.svg",
     "finding": "5 flat colours, budget 3", "fix": "reduce or justify", "evidence": "script"}
  ],
  "summary": {"fail_must": 0, "fail_should": 1, "review": 0, "waived": 0}
}
```

### Exit codes (all three scripts)

| Code | Meaning |
|---|---|
| 0 | Ran; no unwaived MUST failure |
| 1 | Ran; at least one unwaived MUST failure (including a file refused under `brd:SEC-01`) |
| 2 | Usage or input error (bad path, unreadable brief, `--out` outside the brand folder, a bad `--sizes`) |
| 3 | An optional dependency the requested action needs is missing |

A file that does not parse is a `brd:CTR-01` `fail` (exit 1), not an input error.

## brdcheck.py

Deterministic checks of SVG files, the brief's palette and an icon set. Standard library only (`xml.etree.ElementTree`, `re`, `math`, `json`). A directory argument is searched recursively for `*.svg`.

```
python3 brdcheck.py <svg-or-dir>... [--brief brand/brief.md] [--grid-unit N] [--icons brand/icons] [--exports brand/exports] [--stage auto|concept|kit] [--out brand/checks/check.json] [--root DIR]
```

`--grid-unit` overrides the brief's `grid-unit` (concepts carry their own unit in `notes.md` until one is picked).

`--stage` says how far the brief has come. `kit` runs every brief rule. `concept` prints the brief-level rules that need sections written later (`brd:POS-02` rationale lines, `brd:POS-05` story, `brd:TYP-01` empty `wordmark-font`) as `n/a` with the reason, not `fail`. `auto` (the default) picks `concept` when the brief's `## Palette roles` table has no rows, else `kit`. A brief with no roles table at all is therefore `concept` under `auto`; pass `--stage kit` to force the failures.

Each check has one owning rule; the Rule column names it.

| Rule | Check | Status on failure |
|---|---|---|
| `brd:CTR-01` | Text before `<svg` or after `</svg>` (prose, code fences); XML parse; root namespace `http://www.w3.org/2000/svg`; `viewBox` with four finite numbers; any `NaN` or `Infinity`; element bounds (rect, circle, ellipse, line, polyline, polygon, path with transforms applied; arcs use their exact extrema, other curves their control points, so bounds can be slightly generous) outside the viewBox | fail |
| `brd:CTR-02` | Elements `animate`, `animateMotion`, `animateTransform`, `animateColor`, `set`, `mesh`, `meshgradient`, `meshrow`, `meshpatch`, `hatch`, `hatchpath`, `solidcolor`, `discard`. `script` is not checked here (owned by `brd:SEC-01`). Plain `href` (SVG 2) is accepted because all target renderers read it | fail |
| `brd:CTR-03` | No `<title>`; group ids that look generated (`g1`, `path123`, `Layer_1`); (the file-name check is not implemented in 0.1.0) | fail (title), review (ids) |
| `brd:CTR-04` | `image`, `filter` or any `fe*`; `href`, `xlink:href` or `url()` not starting with `#`, and `@import` or `url()` inside a `<style>` element; `text`, `tspan`, `textPath` (reported with `brd:TYP-01` on the same line) | fail |
| `brd:CTR-05` | A file with `linearGradient` or `radialGradient` and no gradient-free `mark.svg` beside it | fail |
| `brd:CAP-01` | Distinct fill and stroke colours (attributes and inline `style`, normalised to 6-digit hex, `none`, `currentColor` and gradient references excluded) over `max_master_colours`. Everything inside `<mask>` and `<clipPath>` is ignored: a matte is luminance, not painted colour | fail |
| `brd:CAP-03` | Any number with more than `max_decimals` decimals: fail. A path with more than `anchor_review` anchors: review | fail, review |
| `brd:CRF-03` | Line and polygon segment angles within `near_angle_window_deg` of, but not equal to, an angle in `exact_angles_deg` or 0 or 90: review. A segment within `angle_tolerance_deg` of an exact angle counts as exact (endpoints rounded to `max_decimals` sit about 0.01 degrees off). Coordinates not a multiple of the grid unit: review (only when a grid unit is known from `--grid-unit` or the brief) | review |
| `brd:CRF-04` | Bounding-box centre offset from the viewBox centre and padding per side, reported as numbers only when the offset exceeds `centre_tolerance_pct` of the viewBox (silent otherwise). Stroke width counts toward the bounds; a rect that fills the whole viewBox is a background and is left out of the numbers | review |
| `brd:TYP-01` | Any `text`, `tspan` or `textPath` in any file (cited with `brd:CTR-04`); a `wordmark*.svg` or `lockup*.svg` with no `path` in its `wordmark` group; with `--brief`, an empty `wordmark-font` when a wordmark file exists | fail |
| `brd:SET-01` | Across every file in `--icons`: different `viewBox`, or different root `stroke-width`, `stroke-linecap`, `stroke-linejoin`, `fill`; values that disagree with `style-spec.json` | fail |
| `brd:SET-02` | `style-spec.json` missing, invalid JSON, or missing any of `grid`, `strokeWidth`, `strokeLinecap`, `strokeLinejoin`, `cornerRadius`, `padding` | fail |
| `brd:SET-03` | A colour value other than `currentColor` or `none` in an icon (the weight half is judgment) | fail |
| `brd:SEC-01` | A `<!DOCTYPE` or `<!ENTITY` declaration (file not parsed further); `script`, `foreignObject`, any `on*` attribute, `javascript:` anywhere in an attribute, a `data:` URL whose media type is not `image/png`, `image/jpeg`, `image/gif` or `image/webp`; every cause found is listed | fail |
| `brd:EVD-02` | With `--brief`: WCAG 2.x relative-luminance contrast for each `text` colour against each `background` (below `contrast_text`: fail), each `ui` colour against each `background` (below `contrast_large_or_nontext`: fail), each `mark` colour against each `background` (reported, status review, because a brand logo may be exempt); a brief with no usable `palette` line gives status `n/a`; a mark pair carries the fix "report only" | fail, review, n/a |
| `brd:EVD-02` (widened) | With a `## Palette roles` table in the brief: `text` and `neutral` against `background` at `contrast_text`; `brand`, `brand-2` and every `status` at `contrast_large_or_nontext`; light on light and dark on dark, never rounded | fail |
| `brd:PAL-01` | Roles table: `brand`, `neutral`, `background`, `text` present, each row with two valid hex values and a ramp entry `<name> <light step>/<dark step>`; an unknown role name is reported and counted as a brand hue. With no table, the old one-line palette path runs instead | fail, review |
| `brd:PAL-02` | OKLCH hue of each brand role (`brand`, `brand-2`, unknown roles) grouped within `same_hue_window_deg`; more groups than `max_brand_hues` fails; two roles in one group are reported as one hue | fail, review |
| `brd:PAL-03` | Within one ramp name, OKLCH lightness must fall as the step number rises, for the light values and for the dark values | fail |
| `brd:PAL-07` (script half) | A `category-colours` entry marked `break` whose hue lies within `same_hue_window_deg` of a brand hue | fail |
| `brd:PAL-08` | Every fill or stroke colour in a file is a role value (light or dark) or a one-line palette value; files with `mono` or `gradient` in the name are exempt; skipped when the brief has no roles table. A `brand-sheet.md` beside the brief is also read: a hex value in it that is not a role value, palette-line value, category colour, black or white is reported as `review` (a stale sheet) | fail, review |
| `brd:EVD-03` | `brand` against `brand-2`, and every two `status` rows: contrast below `contrast_large_or_nontext` is reported for the reviewer to close with a named non-colour cue; when the brief's declaration has a `pair-cue:` line that is not a placeholder, the review becomes a `pass` that names the cue (`brd:EVD-04` is unaffected) | review, pass |
| `brd:EVD-04` | The same pairs after Machado 2009 severity 1.0 simulation (deuteranopia, protanopia, tritanopia) in linear RGB, then Oklab distance; below `cvd_min_oklab_distance` fails for deuteranopia and protanopia and is reviewed for tritanopia | fail, review |
| `brd:POS-05` | `## Story` has between 1 and `max_story_paragraphs` paragraphs (blank-line separated; HTML comments and `<placeholder>` paragraphs do not count): none or too many `fail` (SHOULD); a draft (`story-status` not `confirmed`) is a `review` | fail or review (SHOULD) |
| `brd:POS-01`, `brd:POS-02` | Brief keys `positioning` and `own-word` present and not placeholders; `## Rationale` has a `- <tone word>:` line per tone word plus `- palette:` and `- type:`; none of these fields present gives `n/a` | fail, n/a |
| `brd:CTR-06` | With `--exports`: the check reads the files and trusts nothing the manifest claims. The folder and a well-formed `manifest.json` exist; each stem is a safe name and resolves inside the folder; `svg/<stem>.svg` and `png/<stem>-<size>.png` exist for every size in `export_sizes_px`; each PNG is a valid PNG whose width equals its size; the exported SVG equals `brand/<stem>.svg`; the 64 px PNG has an opaque-pixel share below `export_background_coverage` unless the stem is a tile (tile status is a naming convention: stems starting `app-icon`, `social` or `favicon`, or containing `-tile`); every top-level `brand/*.svg` is exported; a valid `.zip` holds every `svg/` and `png/` file | fail (MUST) |

Outlined lettering (a group or path whose id starts with `wordmark` or `glyph`, honoured only in a file named `wordmark*` or `lockup*`, so a mark cannot hide paths behind such an id) is font geometry: it counts for bounds but is skipped by the `brd:CRF-03` angle and grid checks and the `brd:CAP-03` anchor review. Inside a scaled group (a mark scaled in a lockup) the grid check is skipped too, because the mark keeps the grid of its own coordinates; angles are still checked. The JSON lists the rules run on every file under `rules_checked`, the brief rules under `brief_rules_checked` and the exports rule under `exports_rules_checked`, so a rule that ran and passed is distinguishable from one that did not run; the text output prints only findings, with that list on its first line.

`--icons` also runs `brd:SEC-01`, `brd:CTR-04`, `brd:TYP-01` and `brd:CTR-01` on every icon file. Thresholds read from `thresholds.md`: `max_brand_hues`, `same_hue_window_deg`, `cvd_min_oklab_distance`, `export_sizes_px`, `max_master_colours`, `max_decimals`, `exact_angles_deg`, `near_angle_window_deg`, `angle_tolerance_deg`, `anchor_review`, `centre_tolerance_pct`, `contrast_text`, `contrast_large_or_nontext`.

The Machado 2009 matrices (severity 1.0, Table 1 on the authors' page, read 2026-11-19) and the Oklab matrices (Ottosson 2020) are encoded in the script and tested against published values (white is (1, 0, 0) in Oklab; red is (0.628, 0.2249, 0.1258)) and against the property that each matrix row sums to 1. The judgment half of PAL, POS and TYP rules (harmony, meaning, positioning content, type claims) is read by the reviewer.

Not covered (render or judgment): `brd:CAP-02`, `brd:CRF-01`, `brd:CRF-02`, `brd:CRF-05`, `brd:CRF-06`, `brd:TYP-02` to `brd:TYP-04`, `brd:EVD-01`, and the DEC, CNC and LGL families.

Optional dependencies: none.

## brdrender.py

Renders the PNGs the render rules need. Wraps an external renderer for rasterising; post-processes the PNGs with the standard library.

```
python3 brdrender.py <svg> [--sizes 16,32,64] [--out brand/renders] [--export] [--root DIR]
```

- **Output folder.** Default `brand/renders`. A file inside `brand/concepts/<x>/` renders into `brand/concepts/<x>/renders` instead: every concept is named `concept.svg`, so a shared folder would let one concept's renders overwrite another's. An explicit `--out` wins.
- **Renderer detection.** Use `resvg` if on `PATH`, else `rsvg-convert`; `--renderer` forces one. Neither found: exit 3 with "install resvg or rsvg-convert" (detection runs after the pre-check). The chosen renderer and its version go in the JSON and should be copied to the brief's `tools` field.
- **Pre-check.** Run brdcheck's `brd:SEC-01`, `brd:CTR-04` and `brd:CTR-01` checks first (a file that does not parse cannot be rendered); if any fails, render nothing and exit 1, even when no renderer is installed. A renderer is never handed a file with external references.
- **Mono and reversed: luminance threshold, not colour replacement.** Replacing every fill with black would turn a white shape painted over a black one into a solid disc. Instead: render the unmodified file to RGBA, composite it on white, convert each pixel to luminance (WCAG relative luminance), and set it to black below 0.5 and white at or above (the 0.5 cut is an assumption; move it to thresholds if kept). The inverted image (`-mono-inverted`) is the exact inverse of the mono image. PNG decode and encode use `zlib` and `struct` only (8-bit RGBA, non-interlaced, which both renderers write; anything else: exit 2 with the PNG type found).
- **Dark sources.** When the source stem has a `reversed` or `dark` word (the match brdcheck uses for the dark column of `brd:PAL-08`), the size PNGs and the display PNG are rendered on a neutral dark background (`resvg --background`, `rsvg-convert -b`) so light ink is visible. The mono probe, the variants and every `--export` PNG stay transparent.
- **Paths.** Render paths are printed and recorded as given (relative to `--out` or the root), never through a resolved symlink target. The containment check still uses the resolved path, so a link that leaves the brand folder exits 2.
- **Outputs.** Never edits the source. Any unexpected error prints one line and exits 2, never a stack trace. `rot90` assumes a roughly square viewBox; a non-square mark clips. The JSON `<out>/<stem>-render.json` has the shared shape (`files`, `findings`, `summary`).

| Output | Made by | Rules |
|---|---|---|
| `<stem>-<size>.png` for each size in `test_sizes_px` (default) | Render as is | `brd:CRF-02`, `brd:CAP-02`, `brd:EVD-01` |
| `<stem>-mono.png` | Luminance threshold of a 256 px render, black on white | `brd:CRF-01` |
| `<stem>-mono-inverted.png` | Inverse of the mono image (not `-reversed`: that name belongs to a real `<stem>-reversed.svg` and its renders) | `brd:CRF-01` |
| `<stem>-mirror.png`, `<stem>-rot90.png`, `<stem>-rot180.png` | A wrapping transform on a copy of the root content | `brd:CRF-05` |
| `<stem>-display.png` | Render at 512 px wide, for wordmarks and lockups | `brd:TYP-03`, `brd:CRF-06` |

- **Export mode (`--export`).** Writes the downloadable set for one file instead of the check renders: `<out>/svg/<stem>.svg` (a copy), `<out>/png/<stem>-<size>.png` for each size in `export_sizes_px` (default out `brand/exports`), and merges an entry into `<out>/manifest.json` (`svg`, `png` per size, `transparent`, `tile`). Transparency is the share of non-transparent pixels in a 64 px render, compared with `export_background_coverage` (a full-bleed background covers almost every pixel; ink on a tight viewBox does not, and corner pixels are not used). A non-tile export with a background prints `fail brd:CTR-06` and exits 1. `--sizes` for an export must include every `export_sizes_px` value. Tile status uses the same naming convention as `brdcheck` (`is_tile`). The zip bundle is made with `python3 -m zipfile -c`.
- The script reports the files it wrote, all with status `review` and `evidence: render`: looking at them is the reviewer's job. It decides nothing about craft.
- Exit 0 when all renders were written; 1 when the pre-check failed; 2 or 3 as shared.

## brdtext.py

Turns the brand name into outlined, kerned glyph paths from a font file.

```
python3 brdtext.py --font <file.ttf|otf> --text "<name>" [--size 96] [--tracking 0] [--weight 700] [--opsz N] [--no-harfbuzz] [--out brand/wordmark.svg] [--root DIR]
```

`brd:TYP-07` glyph coverage: a character of the text with no glyph in the font (spaces excepted) exits 2 with `brd:TYP-07` on both shaping paths, since harfbuzz would otherwise draw `.notdef`; a covered name adds a `brd:TYP-07` pass to the record. `--tracking` is extra space between glyphs in font units. `--weight` picks a weight from a variable font's `wght` axis (an instance is cut in a temporary folder; a static font or a weight outside the axis range exits 2); without it a variable font is read at its default weight. `--opsz` sets the `opsz` axis of a variable font; a value outside the axis range is clamped and reported as a `brd:TYP-03` review line, and a font with no `opsz` axis ignores it with the same kind of line. `--no-harfbuzz` skips `uharfbuzz` even when installed (Latin-1 only; used by the tests). Checks run in this order: `--out` location, font file exists (exit 2), `fontTools` installed (exit 3), shaping needs. Only the first font in a collection is read; the licence fields come from the first name record of ID 13 and 14, whatever its platform. The record also goes to `<out stem>.json` beside the SVG.

- **Dependencies.** Two optional packages, `pip install fonttools uharfbuzz`. `fontTools` is needed: without it, exit 3 with that command. `uharfbuzz` is used for shaping when installed; without it the script prints a `brd:TYP-03` review line that kerning was not applied by uharfbuzz and to install it. Without `uharfbuzz`, it accepts only Basic Latin and Latin-1 text (other text: exit 3 with "install uharfbuzz for this script"), lays glyphs by advance width and applies pair kerning from the font's GPOS pair adjustments or `kern` table when present, and records `shaping: none`.
- **Output.** One SVG with a `<title>`, a `wordmark` group, one `path` per glyph (ids `glyph-<n>-<char>`), coordinates at `max_decimals`, a viewBox fitted to the outline bounds, no `<text>`.
- **Record.** The JSON and an XML comment in the SVG hold font family, version, the font's licence name and URL fields (name IDs 13 and 14), the shaping used and the tracking. The licence field is a hint for `brd:TYP-02`, never proof.
- **Rules.** `brd:TYP-01` (outlines produced; font recorded): pass when written. `brd:TYP-02`: status review with the licence string found. `brd:TYP-03`: status review, "inspect pairs on the display render".
- Exit 0 on success; 2 or 3 as shared. It never downloads a font.

## brdinuse.py

Writes `brand/applications.html`: the kit placed in a phone app, a browser tab (light and dark), an app icon at three sizes, a web page, a dark card, a slide and a flyer, then a table of every colour pair in those places with its measured ratio and floor, and a short table of colours the roles table does not offer as text. The page chrome is neutral white; brand colours and the declared type family appear only inside the mocks. Standard library only; the only imports besides it are `brdcheck` (brief parsing, `contrast`, `load_thresholds`).

```
python3 brdinuse.py [--root DIR] [--brief brand/brief.md] [--brand brand] [--out brand/applications.html]
```

- **Inputs:** the brief's `## Palette roles` table (`brand`, `neutral`, `background` and `text` need a valid `#RRGGBB` in both columns; `brand-2` and `status` rows are used when present), the `name`, `concept` and `own-word` lines, and the first family on the `type:` rationale line. From the brand folder: `mark.svg` (required) and, when they exist, `mark-reversed.svg`, `lockup-horizontal(-reversed).svg`, `lockup-stacked.svg`, and `exports/png/mark-16.png`, `mark-32.png`, `mark-reversed-16.png`, `mark-reversed-tile-128.png`. A missing optional file gets a fallback and a printed note.
- **Floors:** `contrast_text` for text and `contrast_large_or_nontext` for large text, icons and UI components, from `thresholds.md`. The browser tab colours (`#FFFFFF`, `#14232F`) are assumed, not brand colours.
- **Output rules:** logos and PNGs are embedded as `<img>` data URIs, so a hostile SVG cannot run script in the page; every brief value is HTML-escaped; the page has no external fonts, scripts or links, and one inline script that hides the intro when the URL has `?embed` (how `index.html` embeds it). A file over 2 MB is not embedded. At 600 px and below the tables stack, one cell per line. Each status row has its own text label that includes the ramp name, and a different icon shape, so two statuses never differ by colour alone.
- **Story:** the page opens with the brief's `## Story` paragraphs (escaped, at most `max_story_paragraphs`, with a note when there are more), and a draft note unless `story-status` is `confirmed`. With no story it shows labelled facts quoted from the brief (`audience`, the essence tension, `concept`, `own-word`, `metaphor`, the palette part of `assets`, the `type:` rationale line, `tone`), skipping any that are empty.
- **Findings:** each pair below its floor prints `fail brd:PAL-09 <group>: <what> <fg> on <bg> is <ratio>:1, floor <n>:1` (at most 30 lines) and is flagged on the page. This is a SHOULD, so the exit code stays 0.
- **Exit codes:** 0 page written; 2 usage or input error (missing brief, roles or `mark.svg`, `--out` not an `.html` file inside the brand folder).
- The copy on the page is placeholder text, and the page says so. The status icon is a tick for a ramp named like `ok`, `success`, `pass` or `green`, then a cross, then a dash for any other.

## brdlive.py

The live page of a `/brand-create` run: one browser tab shows the run as it happens and, at the end, is the brand design brief. Standard library only; the only import besides it is `brdcheck` (brief parsing, `contrast`). Files, all inside `brand/`: `index.html` (the page, with the state embedded so it still opens as a snapshot), `live/state.json`, `live/answers.json`, `live/server.json` (pid and port; never served). The page template is `templates/live-page.html`.

```
python3 brdlive.py [--root DIR] start [--port 8765] [--no-open]
python3 brdlive.py [--root DIR] step <id> pending|active|done|skipped [--note TEXT]
python3 brdlive.py [--root DIR] say <text>
python3 brdlive.py [--root DIR] ask <id> --text T --suggest S [--option V ...] [--kind choice|text|pick]
python3 brdlive.py [--root DIR] wait <id> [--timeout 540]
python3 brdlive.py [--root DIR] answer <id> <value>
python3 brdlive.py [--root DIR] recommend a|b|c <reason>
python3 brdlive.py [--root DIR] refresh | finish | stop | status
```

- **start:** creates `brand/live/`, writes the page, serves `brand/` on `127.0.0.1` (first free port from 8765), prints the URL, opens the browser unless `--no-open`, and runs until `stop`. Run it in the background. A second `start` while one is alive prints the URL and exits 0.
- **Steps:** `brief`, `shortlist`, `concepts`, `review`, `pick`, `kit`, `final` (the brand sheet, the export set and the final review, kit steps 7 to 9). Every command that changes state rebuilds `state.json` and `index.html` from the live state plus a scan of the folder (brief, concepts, SVG files, exports, checks, `review.md`, `brand-sheet.md`, `applications.html`), so the page shows whatever files exist. `start` on a new run marks `brief` in progress. Marking a step `done` or `skipped` (or answering `pick`) starts the next pending step when no other step is in progress, so the page never sits idle between steps.
- **say:** posts a progress message (up to 400 characters) on the step in progress, the latest one started; the page shows it under "Working on". It first starts the next pending step if none is in progress, and exits 2 when no step is left.
- **Questions:** `ask` puts a question on the page with a suggested answer; `--option` makes it a choice and `--kind pick` (id `pick`) shows the concept cards with a Pick button. After `ask ok` it prints the same question, its suggestion and options, as a line to repeat in the terminal, so the user can answer in either place. The user answers in the page (a `POST /api/answer`) or with `answer`; `wait` blocks until the answer is in `answers.json` and prints `{"id":..,"answer":..}`. Exit 3 on timeout; the question stays open.
- **finish:** marks the run done; the page becomes the report (title "Brand design brief", the plugin named in the eyebrow, progress moved to an appendix).
- **Safety:** the server binds `127.0.0.1` only, serves only files under `brand/` (no directory listing; `live/server.json` and lock or temp files return 404), and accepts `POST /api/answer` only with the per-run token from `/api/state` in the `X-Brd-Token` header and, when an `Origin` header is sent, only from the page's own origin. Bodies over 20 000 bytes are refused. Every value shown on the page is HTML-escaped.
- **Concurrency:** state changes are written atomically under a lock file (`fcntl`, so macOS and Linux only).
- **Exit codes:** 0 done; 2 usage or input error (including a missing template or `--root` that is not a directory); 3 `wait` timed out.

## Hardening notes (0.2.0)

- A folder argument skips `concepts`, `exports`, `renders`, `checks` and `icons`, and matches `.svg` case-insensitively.
- `--out` must be a file path; a folder exits 2.
- A processing instruction other than the XML declaration fails SEC-01; CSS escapes are decoded before the url and `@import` scan; `style` attributes and `<style>` blocks are read for colours (`fill`, `stroke`, `stop-color`, `flood-color`, `color`); nesting too deep to walk fails CTR-01.
- Roles and Rationale headings match at any level, case-insensitively, with an optional colon. Hex values must be exactly `#RRGGBB`. Duplicate roles (except `status`), unknown roles and invalid hex on a known role are PAL-01 findings; when a required role is missing, the rules that depend on it report `not run`.
- TYP-05 reads families from the `type:` rationale line (before the first full stop, split on `+`): more than `max_type_families` is `review`, two or more over is `fail`. TYP-06 fails when the line states a smallest size below `min_text_px`.
- POS-01 rejects placeholders (`TBD`, `todo`, `n/a`, `none`, `...`) and a `positioning` statement under six words.
- PAL-08 picks the column from the file name: a stem with a `reversed` or `dark` word is checked against the roles table's dark column, every other stem against the light column and the palette line. A colour from the other column fails, and a file must carry the `brand` or `text` value of its own column as its ink. Mono and gradient stems stay exempt. The name is a convention, like tile names.
