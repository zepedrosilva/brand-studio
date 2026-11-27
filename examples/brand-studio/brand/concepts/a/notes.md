# Concept A

Concept: a drafting compass mid-arc, the instrument of careful construction drawing the one circle everything is built on.

## How the form carries it

An upright compass (hinge disc, handle, two tapered legs at 30 degrees either side of vertical) stands with its needle at the centre of a circle and its pencil on the circle. The circle is only part drawn: a 135-degree arc runs from the pencil tip down and round to the left, so the mark shows construction in progress. The geometry is honest: the arc is centred exactly on the needle tip, and its radius is exactly the leg spread (96).

## Construction

- viewBox 0 0 256 256; grid unit 8; the symbol is offset 4 down (translate) so top and bottom padding match.
- Primitives: 1 rect (handle), 1 circle (hinge, r 24), 2 polygons (legs), 1 short path (annular arc, outer r 104, inner r 88, so the arc is 16 thick). Fill #000000 only, no strokes.
- Angles: legs at 30 degrees off vertical; the arc ends at 0 and 135 degrees. Points derived from those angles carry 2 decimals and sit off the 8 grid.

## Self-check (3 rounds)

- brd:CTR-01..05, brd:CAP-01, brd:CAP-03, brd:TYP-01, brd:SEC-01, brd:CRF-04: pass [script]
- brd:CRF-03: review [script]: 24 coordinates sit off the 8 grid. They are on exact 30, 45 and 135 degree constructions, so the angles are exact and only the snapping is off.
- brd:CRF-01: pass [render]: the mono and inverted renders read the same. No painted white.
- brd:CRF-02 / brd:CAP-02: review [render]: reads at 32 and 64 px. At 16 px the arc and hinge survive, but the leg tips thin to about 1 px and the compass becomes a blob with a hook.
- brd:CRF-05: pass [render]: the mirror and the 90/180-degree rotations are not a spinner, a play button or a known mark I recognise.
- brd:PAL-08 (concept black not in the palette): not applicable yet, because the palette comes at kit step 2.

## Resemblance noticed

At 32 px the arc plus the pointed legs can read as an undo/refresh arrow. A compass on its own is generic; there is no set square, so it stays clear of the square-and-compasses emblem.

## Edit round 1 (after review)

The existing file was edited, not redrawn. The arc is now 24 thick (outer r 108, inner r 84) and runs a full 180 degrees. The legs are blunt trapezoids, 32 wide at the hinge and 12 at the tip. The pencil-leg tip overlaps the start of the arc. The hinge is smaller (r 20), and the symbol is translated (16 4) so the padding is about 16 to 20 on every side.

- brd:CRF-02: improved, still review [render]. At 16 px it reads as a bowl with a small peak, not a squiggle, but the compass itself is only about 2 px wide. At 32 px it reads.
- brd:CAP-02: pass [render]. The leg-to-arc gap is gone: the pencil leg and the arc are joined.
- brd:CRF-04: the weight is better balanced. brdcheck passes it [script].
- brd:CRF-05: the 180-degree rotation still reads somewhat like a check mark under a dome.
- brd:CRF-03: 40 coordinates are off the 8 grid, all from exact 30-degree constructions [script].
