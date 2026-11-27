---
status: accepted
date: 2026-11-27
---

# No hosted image or vector generator

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, design question 2).

## Context and problem statement

Hosted models can write vectors (Recraft, QuiverAI) or images to trace, and give better organic shapes and text placement. They also cost money per image and carry ownership terms that vary by plan (research, "Technology differences"). Should the plugin use one?

## Considered options

- LLM-written SVG only, checked and rendered locally
- A hosted vector model as the engine
- Diffusion images traced into SVG

## Decision outcome

Chosen option: LLM-written SVG only, because it is free, the user owns the output, and the checks make it reliable for flat marks. Tracing gives node bloat and lost geometry. The concept step is the adapter point if a hosted engine is ever added; using one would be declared in the brief and trigger `brd:LGL-03`.

### Consequences

- Good, because there are no API keys, no per-image cost and no third-party ownership terms.
- Bad, because organic and illustrative marks are out of reach.
