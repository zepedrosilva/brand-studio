# Kit steps

After the pick, in this order. Each step edits or copies `brand/mark.svg`; none redraws it. Run only the steps the brief's `scope` includes. Sources cite `research/brd-research.md` (`A<n>`) and `research/brd-colour-type-research.md` (`C<n>`, `T<n>`).

| Step | Scope |
|---|---|
| 1 Variants | A, B, C (dark variants: C) |
| 2 Palette | B, C (A stays one colour, no ramps) |
| 3 Wordmark | B, C |
| 4 Lockups | B, C |
| 5 Icon set | C, or on request |
| 6 Extras: favicon, app icon, social | A (favicon strip only), C |
| 7 Brand sheet | B, C (A gets the legal block and the Downloads list only) |
| 8 Export | A, B, C (always) |
| 9 Final review | all |

## 1. Variants

- `mark-mono.svg`: one colour (black) on a transparent background.
- `mark-reversed.svg`: the same forms on a transparent background, with no background rect: drawn in white (scope A, B), or in the dark role values (scope C and any kit with a `## Palette roles` table; redraw it after step 2). Every colour must be a declared value (`brd:PAL-08`).
- `mark-reversed-tile.svg` (optional): the reversed mark on a dark background rect, for previews only; the `-tile` name keeps it exempt from the transparency check (`brd:CTR-06`).
- A small-size variant only if the 16 px render loses detail (`brd:CAP-02`), named `mark-small.svg`.
- Scope C: show the dark set on the brand sheet.

## 2. Palette

Method and evidence: `brand-core/references/colour.md`. Never pick or defend a hue by its meaning (`brd:PAL-06`).

1. **Category clichés.** List the category's 2 to 4 common colours (a kit choice, assumption) and write each to `category-colours` as `follow` (a distinct shade) or `break` (with a reason); mark them `assumed` when not checked (`brd:PAL-07`; C24).
2. **Choose roles.** From the tone words and the concept, choose `brand` (and `brand-2` only with a reason), a `neutral` leaning toward the brand hue, `background` and `text`; `status` only for a brand that ships UI (`brd:PAL-01`, `brd:PAL-02`, `brd:PAL-04`).
3. **Build ramps.** In OKLCH: hold hue and chroma, solve lightness, reduce chroma only to stay in sRGB, write hex (`brd:PAL-03`). Take a light and a dark value per role and fill the brief's `## Palette roles` table.
4. **One-line palette.** Write the master's colours to `palette` with their roles (`background`, `text`, `ui`, `mark`); at most 3 flat colours in the master (`brd:CAP-01`).
5. **Check.** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdcheck.py brand/mark.svg --brief brand/brief.md --out brand/checks/check.json` and fix every failure: contrast in light and dark (`brd:EVD-02`), pairs to tell apart (`brd:EVD-03`), colour-blind distance (`brd:EVD-04`), roles, hues and ramps (`brd:PAL-01` to `brd:PAL-03`). Fix by moving lightness within the ramp first. Logotype text is exempt (WCAG 1.4.3); a mark may be exempt only if its low contrast is brand-mandated, so mark contrast is reported, not failed (A11; C2, C4).
6. **Rationale.** Write the palette line and start one line per tone word in `## Rationale` (`brd:PAL-05`, `brd:PAL-06`, `brd:POS-02`; `positioning.md`). Name `assets`: usually the brand colour with a shape from the mark (`brd:POS-03`).
7. A gradient version is optional and lives beside the flat master as `mark-gradient.svg` (`brd:CTR-05`, `brd:CRF-06`).

**If blocked:** without `brdcheck.py`, compute the ratios and distances by the method in `colour.md`, record the evidence level as `judgment`, and say so on the brand sheet. A pair that cannot reach its floor without losing the tone gets a lightness change first, then a non-colour cue, then a waiver line with a reason; never a silent pass.

## 3. Wordmark

1. Choose a font family from the shortlist in `brand-core/references/type.md` by the tone words (any OFL or Apache family is equally valid); read the family's own licence file and record family, version, licence and where it was read in `wordmark-font` (`brd:TYP-01`, `brd:TYP-02`; A12, A13). Decide case and weight now; they are recorded in item 6 (C29, `type.md`).
2. Outline the name, with the venv python named in `brand-create` step 1 (otherwise `python3`): `<python> ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdtext.py --font <file> --text "<name>" --out brand/wordmark.svg`. For a variable font add `--weight 700` (or the weight the mark needs); without it the font's default weight is used, which is often too light beside a solid mark.
3. Without `brdtext.py` or fontTools, ask the user to outline the text in a font tool (for example a "convert object to path" command) and supply the SVG. Never draw the letters yourself (`brd:TYP-04`).
4. Check glyph coverage: with fontTools installed, `brdtext.py` reports any character of the name the font lacks, diacritics included (`brd:TYP-07`); without it, check the family's character set by judgment and say so. A missing glyph means another family.
5. Render it with `brdrender.py` and inspect each letter pair on the display render; adjust per-glyph offsets by editing the transforms (`brd:TYP-03`; A23, A24).
6. Write the `type` line of `## Rationale` (every family, joined by `+`, then why it fits and any stated text sizes) and finish each tone line with the type choice (`brd:TYP-05`, `brd:TYP-06`, `brd:POS-02`). Never call the face dyslexia-friendly (`brd:TYP-08`).
7. Custom lettering is out of scope in v1: if the user wants it, mark the wordmark "needs a designer".

**If blocked:** no shortlist family fits the tone or covers the name's glyphs: pick any OFL or Apache family that does, read its licence file and record it; if none can be found, ask the user for a font file.

## 4. Lockups

- `lockup-horizontal.svg` (mark left of wordmark) and `lockup-stacked.svg` (mark above). Mark-only use is `mark.svg`.
- Reversed versions, transparent with no background rect, in the dark role values (or white when there is no roles table): `wordmark-reversed.svg`, `lockup-horizontal-reversed.svg` and `lockup-stacked-reversed.svg` (`brd:PAL-08`).
- Define clear space as a multiple of a named part of the mark, and a minimum size per lockup (the idea of clear space, minimum size and a misuse list comes from the rknall skill, paraphrased). Write both to the brand sheet.
- Same checks as the master; lockups contain the outlined wordmark, never `<text>` (`brd:TYP-01`).

## 5. Icon set (scope C or on request)

1. Copy `${CLAUDE_PLUGIN_ROOT}/templates/style-spec.json` to `brand/icons/style-spec.json` and set its values from the mark's geometry (`brd:SET-02`). Defaults are practitioner opinion (jezweb): 24 grid, 2 px padding, 2 px stroke, round caps and joins.
2. Draw icons in batches of about 5, each with the spec's viewBox and root stroke attributes, `currentColor`, coordinates at 2 decimals (`brd:SET-01`, `brd:SET-03`; jezweb).
3. Check the set with `brdcheck.py --icons brand/icons`, then render the batch side by side and compare weight.

## 6. Extras

- **Favicon strip (A, C):** render the mark at 16, 32, 64 px; a full favicon file set (ico 32, SVG, 180 px touch icon, 192 and 512 px PNG, maskable safe area) is practitioner opinion (A18), and Google's minimum is 8 by 8, recommended above 48 by 48 (A19).
- **App icon (C):** a 1024 by 1024 square master with no pre-rounded corners and no text unless essential, plus a dark variant (A17, vendor guidance; verify numbers on the live page).
- **Social image (C):** the horizontal lockup centred on the background colour; no size is set by this kit.

## 7. Brand sheet

First write the story: draft `## Story` in the brief from the finished brief (`brand-core/references/positioning.md`, `brd:POS-05`), set `story-status: assumed`, and show it in the final report for the user to confirm or edit; set `confirmed` only when the user says so. Then fill `${CLAUDE_PLUGIN_ROOT}/templates/brand-sheet.md` into `brand/brand-sheet.md`: the story, concept, positioning statement and word to own, distinctive assets and category-colour choices, files, palette with contrast results, palette roles with light and dark contrast and the colour-blind results (`n/a` when there is no pair to compare), type with its families, sizes and rationale, clear space and minimum size, misuse list, the legal notes block (`brd:LGL-01`) unchanged except for the fill-ins, and the provenance note (`brd:LGL-04`). Scope C adds the full colour-blind report (deutan, protan and tritan per pair, each `review` item resolved in one line) and the dark set. Fill the Downloads list from step 8 (the zip, the `svg/` and `png/` folders, the sizes and the transparency note). Note any evidence gap (a rule checked by judgment only).

## 8. Export (always)

Every scope ends with a downloadable set (`brd:CTR-06`). Concept files from the checkpoint (`brand/concepts/`) stay out of it.

1. If `svgo` is installed, optimise the final files first, record the version in `tools`, and re-run `brdcheck.py` (A22: v4.1.0 tightened XML parsing; the v4 default preset keeps the viewBox). Exporting after this keeps the copies current.
2. For every top-level brand SVG (`mark`, `mark-mono`, `mark-reversed`, `wordmark`, `wordmark-reversed`, every lockup and its reversed version, and any extras), one file per call:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdrender.py brand/<stem>.svg --export`
   It writes `brand/exports/svg/<stem>.svg`, `brand/exports/png/<stem>-<size>.png` at each `export_sizes_px`, and adds the file to `brand/exports/manifest.json`. It prints `transparent: yes|no`. The sizes come from `export_sizes_px` in `thresholds.md`; an export needs at least those sizes.
3. Exit 1 with `brd:CTR-06` means a non-tile file has a background: remove the background rect and export again. Only tiles may keep one: stems starting with `app-icon`, `social` or `favicon`, or containing `-tile`.
4. Bundle: `cd brand/exports && python3 -m zipfile -c <name>-brand-assets.zip svg png`, with `<name>` the brand name in lowercase, hyphenated.
5. Applications (with a `## Palette roles` table): after the exports, run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdinuse.py` from the project root. It writes `brand/applications.html`, a standalone page that places the kit in a browser tab, an app icon, a web page, a dark card, a slide and a flyer, using only the roles table and the kit's own files, and measures every colour pair (`brd:PAL-09`). Each `fail brd:PAL-09` line names a pair below its floor: change the role value or the use, and run again. Keep `applications.html` beside the brand sheet; it is a deliverable, not part of the zip. Without a roles table the script exits 2: say so in the report and name this step as the next one.

**If blocked:** no renderer: install `resvg` or `rsvg-convert` and run again. If that is impossible, hand the user the SVGs, say plainly that the PNGs were not made, and report the verdict as `incomplete` with this step as the next step. Never skip the export silently.

## 9. Final review

- Read `brand/applications.html` first: every pair should clear its floor, and its notes (no reversed mark, no exports folder) must be gone.
- Run `brand-reviewer` on the whole brand folder with `brdcheck.py ... --brief brand/brief.md --exports brand/exports`; it returns the verdict, and the main session writes it to `brand/review.md`. A missing or incomplete export set fails `brd:CTR-06`. The check reads the files, not just the manifest: PNG width and transparency, the zip contents, and that each export copy still matches its master (export again after any edit).
