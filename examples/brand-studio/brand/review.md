# Review: after the recolour

Reviewer: `brand-reviewer` (sonnet, high), 2026-11-27, after the maintainer replaced the brand colour (a burnt orange that read brown) with vermilion #D33222 (light) and #FE5F4B (dark), approved a rewritten story and set the word to own to "checked".

**Verdict: pass with findings.** 0 MUST fail, 0 SHOULD fail [script].

- Every fill in the brand SVGs, icons and exports is a roles-table value; the old brand colour appears in no asset [script].
- brd:PAL-09: 21 of 21 pairs in the regenerated `applications.html` clear their floor [script]. The other colours on that page are its own chrome (pass and fail badges, a mock browser tab), not brand colours.
- brd:CRF-01, CRF-02, CAP-02: the diamond and brackets stay distinct at 16 px and in one colour; the vermilion diamond reads on cream and on dark [render].
- brd:CAP-03, CRF-03 on `social.svg`: outlined lettering on a tile, accepted as before.
- Legal (brd:LGL-02): resemblance to common developer-tool bracket marks; no search was done; not a clearance.

The sections below are the earlier passes, kept as the record; colour values in them are updated where they described the current kit.

---

# Review: final kit

Reviewer: `brand-reviewer` (sonnet, high), on the whole brand folder after the kit. Written by the main session from the returned verdict, 2026-11-27.

**Verdict: pass with findings.** 0 MUST fail, 0 SHOULD fail; 3 script `review` items, all resolved below.

Scope: 13 top-level SVGs (mark, mono, reversed, wordmark and reversed, four lockups, favicon, two app icons, social image), 6 icons and the export set. Scripts: brdcheck with `--brief`, `--exports` and `--icons`; brdinuse output read. Renders: resvg 0.50.0, about 25 PNGs looked at.

## Passing MUST rules

- brd:CTR-01 to CTR-05, CAP-01, SEC-01 on every file [script]. No text, tspan, image, href, style, script or gradient in any SVG or export.
- brd:TYP-01, TYP-02 [script]: the wordmark is outlined; Space Grotesk 2.000, weight 700, OFL-1.1, source commit recorded.
- brd:CRF-01, CRF-02 [render]: legible in one colour, inverted, and at 16 and 32 px; the 1 px channel at 16 px still reads.
- brd:CTR-06 [script]: the export set is complete.
- brd:PAL-01 to PAL-03, PAL-08, EVD-02 to EVD-04 [script]: every fill is a declared role value.

## Findings

- review brd:POS-05: the story is a draft until the maintainer confirms it (a user action, not a defect).
- pass brd:PAL-09: 21 of 21 pairs in `applications.html` clear their floor. Thin margins: neutral #766E6A on #FDF3EF at 4.57:1 (12 px small print) and brand #D33222 on #FDF3EF at 4.53:1; re-run brdinuse after any change to those roles.
- note brd:CAP-02: the channel is exactly 1 px at 16 px, at the limit; clean from 32 px up.
- note brd:CRF-05: no known shape in mirror or rotation; the silhouette can read as an eye.
- note brd:SET-01 to SET-03 [judgment only]: brdcheck did not run the set rules on `icons/`. All six icons share viewBox 24, stroke 2, square caps, mitre joins and no fill, matching `style-spec.json`. Logged as a plugin issue.
- note brd:CNC-03 [judgment]: guesses at the final review were code brackets around a diamond, an eye, a gem in a frame: developer tooling reads, "brand" does not.

## Review items resolved

- brd:CAP-03 and brd:CRF-03 on `social.svg`: dismissed; the anchors and off-grid points are the outlined letters, exempt by design in wordmark and lockup files.
- brd:CRF-01 on the mono render of an already reversed lockup: dismissed as a renderer artefact; the reversed display renders on dark read.
- brd:CRF-02 on the horizontal lockup at 16 px: dismissed; its minimum is 120 px wide, and the 16 px asset is the mark.
- brd:TYP-03, brd:CRF-06: confirmed clean; even letter spacing, no effects.

## Legal (brd:LGL-01 to LGL-03, US only)

Warnings, not decisions. AI-drafted, so copyright may not attach to the mark as drawn. Nobody has checked the mark or the name for trademark clearance: search the USPTO records, including the image search, before relying on it. Space Grotesk is OFL-1.1. Resemblance: generic code-bracket icons, and an eye. Only US notes exist; the brief's jurisdiction is worldwide.

## Run notes

- Two plugin issues found by this run: concept renders overwrite each other because every concept file is named `concept.svg`; and `brdcheck --icons` does not run the `SET-*` rules.

---

# Review: concepts at the checkpoint

Reviewer: `brand-reviewer` (sonnet, high), blind: given the three `concept.svg` files only, not the name, brief or notes. Written by the main session from the returned verdict, 2026-11-27.

## Verdicts

| Concept | Verdict |
|---|---|
| A (drafting compass) | incomplete after one edit round: brd:CRF-02 (MUST) is `review`; before the edit it was `fail` |
| B (branding iron) | pass with findings |
| C (code brackets) | pass with findings |

Scope: 3 files; brdcheck run (0 fail, 0 review; no brief, no font tools); renders run with resvg into `brand/renders/a`, `b`, `c`; check output `brand/checks/review.json`.

## Name test (brd:CNC-03, judgment)

Guesses from the renders alone, before any name was known; scored afterwards by the main session against the narrative.

| Concept | Guesses | Score |
|---|---|---|
| A | compass or dividers drawing an arc; sickle or hook; clock hand or timer | partly (construction reads; the brand idea does not) |
| B | plumb bob or pendulum; map pin or keyhole; key or hanging sign | no (no link to "brand" or to app identity) |
| C | code brackets `<>`; eye; gem or data node | yes (the developer's world reads first) |

## Findings

A
- fail brd:CRF-02 (MUST): the thin arc and tapering legs collapse at 16 px into a squiggle with no compass reading; weak at 32 px. Fix: thicken the arc and legs or add a small-size variant. [render]
- fail brd:CAP-02 (SHOULD): the gap between the leg tip and the arc is about 0.5 px at 16 px and closes. [render]
- note brd:CRF-04: weight lopsided to the upper right. brd:CRF-05: rotated 180 degrees it reads as a lightbulb or check mark.

B
- pass brd:CRF-01, brd:CRF-02 [render]
- review brd:CRF-05 (SHOULD): upright it can read as a pin or key; rotated, a key or signpost. No known mark; the stem on a diamond is generic. [render]

C
- pass brd:CRF-01, brd:CRF-02 [render]
- review brd:CAP-02 (SHOULD): the top gap between the brackets is 16 of 256 units, about 1 px at 16 px; holds in the render but is the tightest point. [render]
- note brd:CRF-05: rotated 90 degrees it forms a hexagonal gem; symmetric, so mirroring changes nothing.

At 16 px: C reads cleanly, B holds as a pin silhouette, A fails. In one colour all three are pure black and read the same on white and reversed.

A after the edit round (designer self-check; brdcheck 0 MUST failures)
- review brd:CRF-02 (MUST): at 16 px it reads as a bowl with a small peak, about 2 px of compass; reads at 32 px. Next step: a simplified 16 px variant. [render]
- pass brd:CAP-02: the pencil leg now joins the arc, so no gap can close. [render]
- pass brd:CRF-04 [script]; review brd:CRF-03: 40 coordinates off the 8 grid, all from exact 30-degree construction.

## Legal (brd:LGL-02)

Resemblance only, not a clearance. C resembles generic code-bracket icons, B generic pin and plumb-bob icons, A generic compass icons. Run the trademark and design-mark searches listed in the brand sheet (US-centred) before relying on any mark.

## Run notes

- The three concept files share the name `concept.svg`, so default renders overwrite each other; the reviewer rendered into per-concept folders. Logged as a plugin issue.
