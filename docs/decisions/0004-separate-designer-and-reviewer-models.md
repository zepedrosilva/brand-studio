---
status: accepted
date: 2026-11-27
---

# Designer and reviewer are separate agents on different models

Recorded after the fact; decided 2026-11-18 when the agents were first built.

## Context and problem statement

A model that grades its own drawing tends to pass it. The concepts also need an honest answer to "does this mark mean anything without its name?". Who reviews?

## Considered options

- A separate, read-only reviewer agent on a different model, blind to the brief at the concept review
- The designer self-checks only
- The main session reviews

## Decision outcome

Chosen option: a separate reviewer (`brand-reviewer`, sonnet, high effort) apart from the designer (`brand-designer`, opus, medium effort). At the concept review it sees only the SVG files, so the name test (`brd:CNC-03`) is blind. `brd:CNC-03` itself was added after a full run in which abstract concepts passed every check and still meant nothing next to the name.

### Consequences

- Good, because findings come from a second model with no stake in the drawing.
- Bad, because a run costs more model calls.
- Bad, because the model names are pinned in the agent files and need a review when models change.
