---
status: accepted
date: 2026-11-27
---

# One checkpoint, then edit rather than regenerate

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, design question 5).

## Context and problem statement

A brand run can ask the user many questions or none. Practitioners report that a hard stop before the kit catches the wrong direction early (A9), and that editing a working SVG beats regenerating it (A10). Where should the user decide, and what happens after?

## Considered options

- One hard checkpoint with three concepts and a recommendation, then the kit is edited from the pick
- An approval at every step
- No checkpoint: generate the whole kit and let the user regenerate

## Decision outcome

Chosen option: one checkpoint, because it puts the user's judgment where it matters most, the idea, and keeps the rest of the run moving. `/brand-create` never continues without a pick; every kit file is an edit of `brand/mark.svg`.

### Consequences

- Good, because variants, lockups and icons stay consistent with the picked mark.
- Good, because the user's selection and edits are recorded, which matters for authorship (`brd:LGL-04`, A14).
- Bad, because a user who dislikes all three concepts starts the concept step again.
