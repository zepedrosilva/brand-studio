---
status: accepted
date: 2026-11-27
---

# Scripts are optional and use the standard library

Recorded after the fact; decided 2026-11-18 during the initial research (`plugin/research/brd-research.md`, design question 4).

## Context and problem statement

Many rules can be checked by a script (parse, structure, contrast, colour-blind distance), and render rules need a raster. Requiring tools would make the plugin hard to install. How hard a dependency are the scripts?

## Considered options

- Optional Python 3 scripts, standard library only, with optional external tools detected at run time
- Required scripts with a package to install
- No scripts: every rule by judgment

## Decision outcome

Chosen option: optional standard-library scripts, because the plugin then installs with nothing extra and every rule still runs. A finding records its evidence level (`script`, `render` or `judgment`), and a render rule without a render cannot pass: its MUST stays `review` and the verdict is `incomplete`.

### Consequences

- Good, because the review is honest about what was proven and what was judged.
- Good, because the scripts are deterministic and tested with fixtures.
- Bad, because a user without `resvg` gets `incomplete` verdicts until they install it.
