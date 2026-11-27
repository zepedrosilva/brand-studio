# Concept B

Concept: the end of a branding iron, a simple geometric seal: the oldest meaning of "brand", a mark made once and made to last.

## How the form carries it

A straight shaft (the iron's rod) runs down into a hollow lozenge (the iron's head, the seal it burns). Read top to bottom it is the tool seen from the side, head down, about to press; the lozenge alone is the mark it leaves. No heat lines, no flame: the idea rests on shaft plus seal.

## Construction

- viewBox 0 0 256 256, grid unit 8; every coordinate is a multiple of 8.
- Two primitives: one `rect` (shaft, 32 x 112, overlapping the head so the joint is solid) and one `path` with `fill-rule="evenodd"` (a 45-degree square ring: outer half-diagonal 72, inner 32, band about 28 units).
- Fill #000000 only; the counter is a hole, not white paint.
- Padding 16 top and bottom (6.25%); sides wider because the mark is portrait. Negative space about 75%.

## Self-check (round 2 of 3)

- brdcheck (concept file only, grid 8): CTR-01..05, CAP-01, CAP-03, CRF-03, CRF-04, TYP-01, SEC-01 pass [script]. With `--brief`, PAL-08 flags #000000 as not in the palette; expected before kit step 2 (SHOULD).
- CRF-02 / CAP-02: 16, 32, 64 px renders keep the shaft and counter open [render].
- CRF-01: mono and inverted read the same; transparent, no painted white [render].
- CRF-05: mirror is identical (symmetric); rot90 reads as a key or pin, rot180 as a signpost; no spinner, play button or known mark seen [render].
- Round 1 had a T crossbar handle; removed because it read as a capital letter T over a diamond.

## Resemblance noticed

Close to a plumb bob or pendant, and to runic and cattle-brand glyphs in general (a lozenge on a stem). Generic, but worth a user-run trademark search (LGL).
