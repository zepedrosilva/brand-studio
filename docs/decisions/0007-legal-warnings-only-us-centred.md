---
status: accepted
date: 2026-11-27
---

# Legal items are warnings, US-centred

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, design question 6).

## Context and problem statement

AI-assisted marks raise copyright, trademark and font-licence questions that existing tools barely mention (A12, A14 to A16). The plugin cannot give legal advice. What does it say?

## Considered options

- A warning block on every brand sheet and review, with sources and recheck dates, leaving every decision to the user
- No legal content
- Pass or fail legal checks

## Decision outcome

Chosen option: warnings only (`brd:LGL-*` never pass or fail), because the user owns the decision and a clearance search is theirs to run. Only US sources were researched, and the notes say so.

### Consequences

- Good, because users learn that prompts alone may not make them the author and that a trademark search is needed.
- Bad, because users outside the US get notes that may not apply; tracked in open questions.
- Bad, because the facts age; each carries a recheck date.
