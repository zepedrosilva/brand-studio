---
status: accepted
date: 2026-11-27
---

# Wordmarks are outlined from OFL or Apache fonts

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, design question 3).

## Context and problem statement

Every source read says live text and model-drawn letterforms fail in logos (A9, A2). A wordmark also has to survive on machines without the font. How are letters made?

## Considered options

- Shaped, kerned outlines from an OFL or Apache font, with the licence recorded
- Letters drawn as paths by the model
- Live `<text>` with a font reference

## Decision outcome

Chosen option: outlines from an open font, because the OFL lets a logo be built from its outlines and the graphic stays the user's (A12), and shaping with HarfBuzz gives correct kerning (A23, A24). Enforced by `brd:TYP-01`, `brd:TYP-02` and `brd:TYP-04`.

### Consequences

- Good, because wordmarks are legible, licensed and render the same everywhere.
- Bad, because `brdtext` needs `fontTools` (and `uharfbuzz` for shaping), the one non-standard dependency.
- Bad, because custom lettering is out of scope; it is marked "needs a designer" (see open questions).
