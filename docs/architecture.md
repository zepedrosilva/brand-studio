# Architecture

Structure and boundaries that the code does not show: why the parts are split this way and what must not depend on what.

## Two halves

- `plugin/` is the product: what `claude plugin install` copies to a user's machine. It must work on its own, so it carries its own research (`plugin/research/`), because the rules cite it by source ID.
- The repository root is the project: docs for contributors, the worked example, the GitHub Pages site and CI. Nothing in `plugin/` may refer to a file outside it.

## One core, two workflows

- `brand-core` owns every shared fact: principles, the rule catalogue, severities, evidence levels, thresholds, the brief format, the brand folder layout, legal notes and the script contract. It is never invoked by the user directly.
- `brand-create` and `brand-review` are workflows that load the core and add only their steps. A fact needed by both belongs in the core, never copied into a workflow.
- `references/thresholds.md` is the single source of every number. Scripts read its YAML block; nobody hard-codes a value.

## Designer and reviewer are separate agents

- `brand-designer` draws one concept; `/brand-create` starts three in parallel, one per metaphor line, so the concepts are independent rather than three variations of one idea.
- `brand-reviewer` runs on a different model and is read-only, so the work is not graded by its author. For concepts it is blind: it gets the SVG files only, never the name, the brief or the designer's notes, so the name test (`brd:CNC-03`) is honest.
- Only the main session talks to the user and writes `brand/review.md`. Agents return text.

## Scripts are helpers, never a gate

- The five scripts in `brand-core/scripts/` raise the evidence level of a finding from `judgment` to `script` or `render`. Every rule still runs without them; a render rule without a render ends as `review`, and a MUST in `review` makes the verdict `incomplete`, never `pass`.
- Standard library only, so the plugin installs with nothing else. The exceptions are optional and detected at run time: `fontTools` and `uharfbuzz` for wordmark outlines, `resvg` or `rsvg-convert` for renders. A missing one exits 3 and the skill falls back to judgment.
- Scripts treat SVG as untrusted data: never executed, never rendered in a browser, no external references followed, and output only inside `brand/`. `brdlive` binds to 127.0.0.1 with a per-run token.

## Output contract

Everything a run writes goes to `brand/` in the user's project, in the layout fixed by `brand-core/SKILL.md`. File names are part of the contract (`brd:CTR-03`): the scripts and the reviewer find files by name.
