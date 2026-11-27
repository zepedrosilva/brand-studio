---
status: accepted
date: 2026-11-27
---

# Concepts are drawn greyscale, primitives first

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`).

## Context and problem statement

Models write SVG reliably only for flat, geometric marks with few shapes; complex paths, text, symmetry and stacking order are where they fail (A1, A2, A4). Colour and effects can also hide a weak form. How should a concept be drawn so it is both buildable by a model and judged on its idea?

## Considered options

- Greyscale concepts built from primitives (circles, rects, polygons, arcs) on a grid, paths only for merged silhouettes
- Free-form SVG in full colour from the start
- A raster image traced into SVG

## Decision outcome

Chosen option: greyscale and primitives first, because it plays to what models draw well and makes the one-colour, 16 px and reversed tests (`brd:CRF-01`, `brd:CRF-02`) meaningful before any colour is added.

### Consequences

- Good, because concepts are small, checkable files and compare on form alone at the checkpoint.
- Good, because colour comes later as declared palette roles, not as decoration.
- Bad, because organic or illustrative marks are out of reach; the README says so under limits.
