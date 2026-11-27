# Brand rule catalogue

Kit code: `brd`. Outside this file, qualify IDs as `brd:<ID>` (for example `Waives brd:CAP-01 for mark.svg: ...`). IDs are never reused or renumbered. Severity, statuses and evidence levels: `severity-and-evidence.md`. Numbers: `thresholds.md`.

Inside the tables below, IDs are unqualified; every one carries the `brd:` prefix elsewhere. Each check has one owning rule; a defect that breaks several rules cites all of them on one finding line.

Detect codes: **S** script-checkable (`brdcheck.py`), **J** judgment, **E** needs a render or a live search. The Source column cites the research brief (`research/brd-research.md`): `A<n>` is a track A source; a name is a track B skill or tool, paraphrased. `C<n>` (track A) and `T<n>` (track B) cite `research/brd-colour-type-research.md`; those rows end with their source label (`severity-and-evidence.md`, "Source labels"). A palette, type or positioning rule decided by judgment is SHOULD or MAY with status `review`, never MUST.

## A. Declaration (DEC)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| DEC-01 | MUST | The brief states the name, a one-sentence concept, the audience, 3 to 5 tone words and a list of things to avoid. | J: read the declaration block in `brief.md`; empty or placeholder fields fail. | Fill the missing fields before drawing; ask the user once for what the narrative does not say. | A9, A27 |

## B. Concept method (CNC)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| CNC-01 | SHOULD | A shortlist of 8 to 12 metaphor one-liners exists, mixing literal and abstract ideas, with the category's clichés named, and the chosen concept is one of them. | J: count the shortlist in `brief.md`; check clichés are listed and the chosen line is marked. | Build and score the shortlist; drop a cliché unless it has a twist. | A9, A27 |
| CNC-02 | SHOULD | The concept can be explained in one sentence. | J: the concept sentence and `notes.md`; two ideas joined by "and" fail. | Cut to one idea. | A9, A28 |
| CNC-03 | SHOULD | Name test: shown alone with no text, a reviewer who has not been told the name can link the mark, at least partly, to the name or the narrative's world (a wave or tide line for a name like Tideline). | J: the reviewer lists its three most likely guesses for the mark and says whether they point to the name or domain (yes, partly, no); `no` fails. A mark may still be chosen on `no` if the user says so at the checkpoint. | Choose or draw a more literal line from the shortlist, or add a cue (a detail only this subject has). | The user's checkpoint objection, 2026-11-19 (own rule, assumption) |

## C. SVG file contract (CTR)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| CTR-01 | MUST | The file parses as XML, has the SVG namespace and a `viewBox`, contains no NaN or Infinity values, has no prose or code fences around the markup, and all content lies inside the viewBox. | S: parse; root attributes; numeric scan; element bounds against the viewBox. | Repair the markup; redraw if the file was truncated. | A7, A5 |
| CTR-02 | MUST | The file uses only the static SVG 1.1 subset: no animation, no SVG 2-only features. Scripts are owned by SEC-01. | S: element lists in `scripts/SPEC.md`; `<script>` is reported under SEC-01, not here. | Remove the feature, or redraw it with primitives. | A20, A21 |
| CTR-03 | SHOULD | The master has a `<title>`, groups with meaningful ids (for example `symbol`, `wordmark`) and a file name from the brand folder layout. | S: `<title>` present, group ids not auto-generated, name matches the layout in the core. | Add the title, rename groups and files. | kaankiziltug, neonwatty |
| CTR-04 | MUST | The master contains no `<text>`, no embedded raster, no filter and no external reference. | S: `text`, `tspan`, `image`, `filter`, `fe*`, any `href` or `url()` not starting with `#`. | Outline text (`brdtext.py` or a font tool); remove or redraw the rest. | kaankiziltug, A9 |
| CTR-05 | SHOULD | Any file with a gradient has a flat-colour master beside it. | S: a gradient in a file and no gradient-free `mark.svg` in the same folder. | Ship the flat master; keep the gradient as an optional extra. | kaankiziltug |
| CTR-06 | MUST | A delivered kit (the final review of scope A, B or C; not the concept checkpoint) has `brand/exports/` made by `brdrender.py --export` with, for every top-level brand SVG (mark, mono, reversed, wordmark, every lockup and its reversed version), an SVG copy and a transparent PNG at every `export_sizes_px`, a `manifest.json` and a zip bundle; only tiles, app icons, social images and favicons keep a background. | S: `brdcheck.py --exports brand/exports` reads the files, not just the manifest: PNG width and transparency, zip contents, and that each export copy matches its master; sizes come from `export_sizes_px` in `thresholds.md`, and an export needs at least those sizes. No folder, no readable manifest, a missing or stale file, a non-tile PNG with a background, a top-level `brand/*.svg` not exported, or a missing or incomplete zip fails. | Run `brdrender.py <svg> --export` for each top-level SVG, remove background rects from non-tile files (or name a tile with `-tile`), then build the zip (`kit-steps.md`, step 8). | The user's instruction, 2026-11-19 (own rule); assumption (the sizes) |

## D. Budgets (CAP)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| CAP-01 | SHOULD | The master uses at most `max_master_colours` flat colours. | S: count distinct normalised fill and stroke colours, `none` excluded; colours inside `<mask>` and `<clipPath>` are not counted (a matte is luminance, not painted colour). | Reduce, or justify the extra colour in the brief. | kaankiziltug (opinion) |
| CAP-02 | SHOULD | No feature is smaller than 1/`min_feature_divisor` of the mark, and no gap closes at the smallest test size. | E: view the 16 px render beside the master. | Thicken, merge or delete the detail; add a small-size variant. | kaankiziltug (opinion), A10 |
| CAP-03 | SHOULD | Paths stay simple: few anchors, coordinates with at most `max_decimals` decimals, circles drawn as circles or arcs. | S: decimals over the limit fail; anchor counts per path and polygonal circle approximations are `review`. | Simplify by hand or with svgo, snap coordinates, replace approximations with `circle` or arcs. | A22, kaankiziltug, jezweb |

## E. Logo craft (CRF)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| CRF-01 | MUST | The mark is recognisable in one colour on white and reversed on dark. | E: view the one-colour and reversed renders beside the master. | Remove the dependence on colour or on tonal contrast between parts. | A9, A28 |
| CRF-02 | MUST | The mark is legible at every size in `test_sizes_px`. | E: view the render strip. | Simplify; provide a small-size variant. | A9, A10, A19 |
| CRF-03 | SHOULD | Key angles are exact (`exact_angles_deg`; horizontal and vertical aside) and dimensions snap to the grid unit declared in the brief. | S: segment angles near but not equal to an exact angle; coordinates off the grid unit. | Snap angles and coordinates. | kaankiziltug |
| CRF-04 | SHOULD | The symbol sits on its optical centre with consistent padding. | S+J: script reports the bounding-box offset and padding per side; judgment decides optical centre (triangles and circles sit differently). | Re-centre; even the padding. | kaankiziltug |
| CRF-05 | SHOULD | Mirrored or rotated, the mark forms no unintended shape (a spinner, a play button, a known mark). | E+J: view the mirrored and rotated renders. | Redraw the part that creates the shape. | A9 |
| CRF-06 | MAY | Effects (gradients, shadows) are not hiding a weak form. | J: compare the flat greyscale version with the effect version. | Remove the effects; strengthen the form. | kaankiziltug |

## F. Lettering and fonts (TYP)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| TYP-01 | MUST | The wordmark is outlines, and the font family, version and licence are recorded in the brief. | S+J: owns lettering. S: any `<text>` in any file (cited together with CTR-04), and every wordmark or lockup is outlines. J: `wordmark-font` records family, version and licence. | Outline with shaped, kerned positions (`brdtext.py`); record the font. | A12, A23, A24 |
| TYP-02 | MUST | The font's licence allows logo use: OFL or Apache, checked for each family. | J: read the family's own licence file; the font's name-table licence string is a hint only. | Pick another family. | A12, A13 |
| TYP-03 | SHOULD | Letter pairs are inspected for kerning and optical spacing after outlining. | E: view the wordmark render at display size, pair by pair. | Adjust per-glyph offsets; note the change. | A23, A24 |
| TYP-04 | SHOULD | No letterforms are drawn by the model, unless the user asked for custom lettering and a human reviews it. | J: the `tools` field and the wordmark's provenance note. | Use an outlined OFL font; mark custom lettering "needs a designer". | A9 |
| TYP-05 | SHOULD | The type system uses at most `max_type_families` families, a third only with a stated role; a second family differs from the first in construction (for example serif against sans), not only in weight. | S: count the families in `wordmark-font` and the `type` line of `## Rationale`. J (`review`): the construction difference. | Drop the extra face, or replace the second with one that does something the first cannot (`type.md`). | C35, C43; vendor guidance |
| TYP-06 | SHOULD | No thin or ultralight weight is used at or below `min_text_px`, and every text size stated in the brief or brand sheet is at least `min_text_px`. | S: stated sizes against the threshold. J (`review`): weights, when no font file is given. | Use a heavier weight or a larger size. | C35; vendor guidance (platform floors differ) |
| TYP-07 | SHOULD | The wordmark font has a glyph for every character of the brand name, diacritics included. | S (optional, fontTools): `brdtext.py` reports a missing glyph. Without it, J (`review`) from the family's character set. | Pick another family; a hand-added glyph needs a designer's review (`brd:TYP-04`). | practitioner opinion (the kit's own) |
| TYP-08 | SHOULD | No claim that a typeface helps readers with dyslexia; type accessibility notes cover spacing, size and plain styles only. | J (`review`): read the brief, the `## Rationale` lines and the brand sheet. | Reword to the spacing, size and style choices (`type.md`). | C30 to C33; weak or contested evidence (controlled studies found no reliable benefit) |

## G. Icon sets (SET)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| SET-01 | MUST | Every icon in a set shares the viewBox, root stroke attributes, grid and padding. | S: compare every file in `icons/` with each other and with `style-spec.json`. | Normalise, or redraw the outlier. | jezweb |
| SET-02 | SHOULD | `icons/style-spec.json` declares grid, stroke width, caps, joins, corner radius and padding. | S: file present with those keys. | Add it from `${CLAUDE_PLUGIN_ROOT}/templates/style-spec.json`. | jezweb |
| SET-03 | SHOULD | Icons use `currentColor` and have balanced optical weight. | S+J: hard-coded colours fail; weight judged on a render of the set. | Replace colours with `currentColor`; adjust heavy or light icons. | jezweb |

## H. SVG safety (SEC)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| SEC-01 | MUST | The file has no `<script>`, no event-handler attribute (`on*`), no `javascript:` URL, no `data:` URL other than a raster image, and no `<foreignObject>`. | S: element, attribute and URL scan. Also a `<!DOCTYPE` or `<!ENTITY` declaration: fail, and stop parsing the file (entity-expansion risk). | Strip them (svgo `removeScripts` after repair), then re-check. | A22 |

## I. Evidence (EVD)

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| EVD-01 | SHOULD | Render checks (small size, one colour, reversed, mirror, kerning) are run on a raster of the final file, not judged from the source text. | E: renders in `renders/` are newer than the SVG and were viewed. | Run `brdrender.py` (or any renderer) and look. | A3, A9 |
| EVD-02 | SHOULD | Every declared text and UI role pair meets its floor, in light and in dark: `text` and `neutral` against `background` at `contrast_text`; `brand`, `brand-2` and `status` against `background` at `contrast_large_or_nontext` (large text, UI and non-text); ratios are computed, never rounded. A brand logo may be exempt (WCAG: only if the low contrast is brand-mandated and the logo is not a control), so mark and logotype pairs are reported, never failed. | S: WCAG contrast ratio for each pair in the brief's `## Palette roles` table (light values on the light background, dark on the dark); with no table, the one-line `palette` (`text` at `contrast_text`, `ui` at `contrast_large_or_nontext`, `mark` reported). | Adjust lightness within the role's ramp, or define a text-safe step of the brand colour (`colour.md`). | A11; C1, C2, C4; standard |
| EVD-03 | SHOULD | Role pairs that must be told apart (`brand` and `brand-2`; any two `status` colours) differ by at least `contrast_large_or_nontext`, or carry a non-colour cue (shape, text, pattern) named in the `## Rationale` section. | S: contrast ratio between the two colours, light and dark; below the floor is `review`, unless the declaration has a `pair-cue:` line (not a placeholder), which turns it into a `pass` that names the cue. J: the named cue closes it. | Add a cue, or move one colour's lightness. | C3, C4; standard (WCAG 2.2 SC 1.4.1, 1.4.11) |
| EVD-04 | SHOULD | The same pairs stay distinct under deutan and protan simulation: Oklab distance of at least `cvd_min_oklab_distance` after simulating each; tritan is reported as `review` only. | S: Machado 2009 severity 1.0 matrices in linear RGB, then Oklab distance, light and dark (method in `colour.md`). | Change lightness first, then hue. | C13 to C16; research (strength stated: widely implemented simulation model) plus assumption (the pass line) |

## J. Legal warnings (LGL)

These never pass or fail. They produce the warning block described in `severity-and-evidence.md`; content and sources are in `legal.md`.

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| LGL-01 | MUST (warn) | The brand sheet carries the legal notes block: copyright status of AI-assisted output, trademark clearance as the user's job, fonts used and their licences. | J: block present and filled in `brand-sheet.md`. | Fill it from `${CLAUDE_PLUGIN_ROOT}/templates/brand-sheet.md`. | A12, A14, A15, A16 |
| LGL-02 | SHOULD | A resemblance to a known brand in the category is flagged with search pointers. | E: user-run searches; the model only names resemblances it notices. | Redraw, or the user proceeds knowingly after a search. | A16 |
| LGL-03 | SHOULD | If a hosted generator was used, its plan, ownership and training terms are recorded. | J: the `tools` field in the brief. | Record the terms; avoid free tiers for a commercial mark. | Recraft docs (track B) |
| LGL-04 | MAY | A provenance note records the human selection, edits and arrangement. | J: provenance section in `brand-sheet.md`. | Add a short note. | A14 |

## K. Palette (PAL)

Method and evidence: `colour.md`. Contrast and colour-blind checks on the palette are owned by `brd:EVD-02` to `brd:EVD-04`; the master's colour count stays with `brd:CAP-01`.

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| PAL-01 | SHOULD | The brief's `## Palette roles` table declares `brand`, `neutral`, `background` and `text` (plus `brand-2` if used, and `status` only for a brand that ships UI), each with a light and a dark hex value and a ramp. | S: required roles present; every row has a valid `#RRGGBB` light and dark value (three-digit hex is rejected) and a ramp entry; no duplicate role except `status`. | Add the missing rows; derive missing values from the role's ramp (`colour.md`). | C34, C38, C39, C41; vendor guidance |
| PAL-02 | SHOULD | The palette has one neutral ramp and at most `max_brand_hues` brand hues (`brand`, `brand-2`); hues within `same_hue_window_deg` of each other in OKLCH count as one. Status colours are not counted. | S: OKLCH hue of each brand row's light value only, grouped by the window; ramps named by `neutral` rows. Dark values are not compared. | Merge or drop a hue, or state why in the palette rationale line. | T2, T5, C39; practitioner opinion (the numbers are assumptions) |
| PAL-03 | SHOULD | Ramps are built in OKLCH: within one ramp, lightness falls as the step number rises, hue and chroma are held (chroma reduced only to stay in sRGB), and contrast is computed from the hex values, never inferred from lightness. | S: lightness order only: OKLCH lightness of every value that shares a ramp, ordered by step; one out of order fails. Held hue and chroma and the gamut are part of the method, not checked. | Rebuild the ramp by the method in `colour.md`. | C9, C10; technical source (C9) and standard in progress (C10, CSS Color 4 Candidate Recommendation Draft) |
| PAL-04 | MAY | Neutrals lean toward the brand hue at low chroma, and dark values avoid a pure black background and pure white text. | J (`review`): read the roles table. | Tint the neutral ramp toward the brand hue; soften the dark extremes. | T1, T2; practitioner opinion |
| PAL-05 | MAY | No harmony scheme (complementary, triadic, 60-30-10) is given as the reason for the palette; a scheme may be named as a generation aid only. | J (`review`): the palette line of `## Rationale`. | Reword the reason from tone, category and lightness contrast. | C18, C52; weak or contested evidence |
| PAL-06 | SHOULD | The palette rationale argues from the tone words and the category, not from a universal colour meaning (for example "blue means trust"). | J (`review`): any claim that a hue means one thing to everyone is a finding. | Rewrite the line from the tone words (`colour.md`, "What the evidence supports"). | C21, C23, C25; weak or contested evidence |
| PAL-07 | SHOULD | `category-colours` names the category's common colours, each marked `follow` (with a distinct shade) or `break` (with a stated reason). | J (`review`): the choice and its reason. S: each `break` colour lies more than `same_hue_window_deg` from every brand hue. | List the category colours and state the choice for each. | C24, C50; research (strength stated: moderate, logo colour and product fit, C24) |
| PAL-08 | SHOULD | Every fill and stroke colour in a master, variant or lockup file, and every hex on the brand sheet, is a declared role value from `## Palette roles` or an entry of the one-line `palette`, taken from the column that matches the file: the dark column for names with `reversed` or `dark`, the light column for every other name. A file also carries the `brand` or `text` value of its own column as its ink. Files with `mono` or `gradient` in the name are exempt; colours inside `<mask>` and `<clipPath>` are not read. | S: with `--brief`, `brdcheck.py` compares each file's colours with the declared values, by column, and looks for the brand or text ink. | Recolour the file to the values of its own column and keep the brand colour as the ink, or declare the colour with a role. | Found in the kit's own test run (the reversed mark kept older colours); practitioner opinion |
| PAL-09 | SHOULD | The kit placed in applications (phone app, browser tab, app icon, web page, dark card, slide, flyer) built only from the roles table: every colour pair in those places clears its floor, 4.5:1 for text and 3.0:1 for large text, icons and UI components. | S: `brdinuse.py` writes `brand/applications.html`, measures each pair and prints `fail brd:PAL-09` for each pair below its floor. | Change the role value, or the use that pairs two roles the table cannot support. | Found in the kit's own test run (the palette passed as swatches, and the pairs in use are what a person meets); practitioner opinion |

## L. Positioning (POS)

Method: `positioning.md`. Tone words themselves stay with `brd:DEC-01`.

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| POS-01 | SHOULD | The brief has a `positioning` line (for, who, that, unlike) and an `own-word`. | S: both keys present and not placeholders. J (`review`): the line names the audience, the category, the benefit and the main alternative. | Draft both from the narrative, mark them `assumed`, confirm with the user. | C47; practitioner opinion |
| POS-02 | SHOULD | `## Rationale` has one line per tone word saying how palette and type express it, plus one palette line and one type line. | S: line count against `tone`. J (`review`): each line names a concrete palette or type choice. | Add the missing lines. | C27, C28, C29, C48; practitioner opinion |
| POS-03 | SHOULD | `assets` names one or two ownable distinctive assets (a colour, a shape, a device), and they appear unchanged in every file. | J (`review`): compare the files against `assets`. | Name them; make the files agree. | C50 (secondary); practitioner opinion |
| POS-04 | MAY | An archetype or personality label is a storytelling aid only, never the reason for a colour. | J (`review`): the `archetype` field and the `## Rationale` lines. | Reword the reason from tone and category. | C48, C49; weak or contested evidence |
| POS-05 | SHOULD | The brief has a `## Story`: one to `max_story_paragraphs` short paragraphs that say who the brand is for, what tension it answers and how the mark, palette and type answer it. Every claim traces to a brief field or a `## Rationale` line; no colour meanings, no superlatives. `story-status` is `confirmed` before release. | S: the section exists, is not a placeholder and is within the paragraph budget; `story-status` is read (`assumed` or unset is a `review`). J (`review`): each sentence traces to the brief, and each of the three beats points at a choice that can be seen in the kit. | Draft it from the finished brief at the final report, mark it `assumed`, and confirm it with the user. | Found in the kit's own test run (the applications page opened without a reason to care); practitioner opinion |
