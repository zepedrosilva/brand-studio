---
status: accepted
date: 2026-11-27
---

# Masters are static SVG 1.1

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, A20 and A21).

## Context and problem statement

SVG 2 is still a Candidate Recommendation, and renderers differ on text, filters and newer features (A20, A21). Logo files also travel into tools and sites the user does not control. What may a master contain?

## Considered options

- The static SVG 1.1 subset: no live text, embedded images, filters, scripts or animation
- Any SVG a browser renders
- SVG 2 features where browsers support them

## Decision outcome

Chosen option: the static SVG 1.1 subset, because resvg, librsvg, browsers and design tools all render it the same way, and it removes the safety risks of scripts and external references. Enforced by `brd:CTR-02`, `brd:CTR-04` and `brd:SEC-01`; colours stay hex in SVG, OKLCH only in docs and tokens.

### Consequences

- Good, because one renderer is enough to prove a file, and files are safe to hand on.
- Bad, because gradients and effects are only optional extras beside a flat master (`brd:CTR-05`).
