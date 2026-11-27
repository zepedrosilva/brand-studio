# Concept C

Concept: code angle brackets holding a single solid shape: a developer's world framing one finished mark.

## How the form carries it

Two heavy 45-degree chevrons (the angle brackets of code) face inward around one solid diamond. The diamond's edges run parallel to the chevrons' inner edges, so the gap is one even channel: the brackets frame, the diamond is the finished mark. Two primitives only (chevron polygon, diamond polygon), filled, no strokes.

## Construction

- viewBox 0 0 256 256, grid unit 8; every vertex sits on the 8 grid.
- Chevrons: tip at x 16 / 240, arms to y 64 and 192, horizontal thickness 40 (about 28 perpendicular, 1.8 px at 16 px).
- Diamond: centre 128,128, half-diagonal 40. Gap to the chevrons 32 on the axis (about 23 perpendicular, 1.4 px at 16 px).
- Padding 16 left and right; the mark is wider than tall (64 above and below).
- Fill #000000 only, no background.

## Self-check (round 1)

- brd:CTR-01..05, CAP-01, CAP-03, CRF-03, CRF-04, TYP-01, SEC-01: pass [script]. 0 MUST failures.
- brd:PAL-08 fail (should): #000000 is not in the brief palette; expected, palette is filled at kit step 2. Brief-level PAL-01, POS-02, POS-05 fails belong to later kit steps, not this concept.
- brd:CRF-02, CAP-02, EVD-01: pass [render]: 16 px reads as two brackets and a dot-diamond; channel stays open.
- brd:CRF-01: pass [render]: mono and reversed both read; the gap is a real hole.
- brd:CRF-05: pass [render]: mirror and 180 are identical (symmetric); 90 reads as a gem or shield badge, no spinner or play button.

## Resemblance noticed

The overall silhouette (pointed hexagon with a centre diamond) can read as an eye. The `<◆>` bracket-plus-glyph pattern is common in developer-tool icons, so distinctiveness is the weak point; worth a trademark image search by the user (brd:LGL).
