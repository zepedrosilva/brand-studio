# Constructing a master

How to draw one mark as primitives-first SVG. Read by `brand-designer`. Rules cited are `brd:` IDs; numbers come from `brand-core/references/thresholds.md`. Sources: `research/brd-research.md` A2, A7, A9, A10 and the kaankiziltug, op7418 and neonwatty skills (ideas paraphrased).

## Canvas

- Square, integer viewBox: `0 0 256 256` unless the brief says otherwise (kaankiziltug uses 256 or 512; practitioner opinion).
- Pick a grid unit that divides the viewBox (for example 8 or 16 on 256), record it in the concept's `notes.md` (the main session copies the picked one to the brief's `grid-unit`), and snap every dimension to it (`brd:CRF-03`).
- Padding of about 4 to 8% of the viewBox on each side (practitioner opinion, kaankiziltug); keep it even (`brd:CRF-04`).
- Leave a lot of empty canvas: about 40 to 50% negative space and 1 or 2 core elements (practitioner opinion, op7418).

## Drawing

- **Black first:** fill `#000000` on no background. Greys only when the idea needs two tones, and then the one-colour render must still read (`brd:CRF-01`).
- **Cut-outs are holes, not white paint:** make a counter or negative shape with `fill-rule="evenodd"` on one path, or a `mask`, never a white shape painted over a black one. Painted white shows as a white blob on coloured or dark backgrounds and in the reversed variant.
- **Primitives first:** `circle`, `ellipse`, `rect`, `line`, `polyline`, `polygon`; a `path` only for a merged silhouette or an arc, kept short (A2). Circles are circles, never many-segment polygons (`brd:CAP-03`).
- **Exact geometry:** angles of 30, 45, 60 or 90 degrees; coordinates with at most 2 decimals (`brd:CRF-03`, `brd:CAP-03`).
- **Stacking order:** draw back to front, one `g` per part with a meaningful id (`symbol`, `counter`, `accent`); models get stacking order wrong, so check it on the render (A2, A4).
- **Masters exclude:** `<text>`, images, filters, gradients, external references, scripts, animation (`brd:CTR-02`, `brd:CTR-04`, `brd:TYP-01`, `brd:SEC-01`).
- **File shape:** markup only, starting `<svg xmlns="http://www.w3.org/2000/svg" viewBox="...">`, with a `<title>`; no prose or code fences in the file (`brd:CTR-01`, `brd:CTR-03`).
- Prefer filled shapes to strokes in a mark; strokes belong to icon sets with a style spec.

## Self-check loop

1. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdcheck.py <file> --brief brand/brief.md --grid-unit <unit> --out <folder>/check.json`, if the script exists.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdrender.py <file> --out <folder>/renders`, if the script and a renderer exist.
3. Look at the renders: the strip at 16, 32 and 64 px (`brd:CRF-02`, `brd:CAP-02`; the 16 to 64 px strip caught vanishing detail in A10), mono and reversed (`brd:CRF-01`), mirror and rotations (`brd:CRF-05`: no spinner, play button or known mark).
4. Fix by editing the file; never start over once the idea reads.

Without the scripts, check the same rules by reading the SVG, and say the evidence is `judgment`; render rules stay `review`. Stop after three rounds (assumption; tune) and report what still fails.

## After the pick

The picked concept becomes `brand/mark.svg`. All later changes (colour, small-size variant, lockups) are edits of that file or copies of it, never a fresh drawing (A10).
