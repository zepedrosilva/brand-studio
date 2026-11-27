# Authoring

How to change the plugin: a rule, a reference, a skill, an agent, a template or a script, and how to version the change. Read it before editing anything under `plugin/`.

## The bar for a change

- It answers a real observed failure or request, ideally an issue with an example SVG or a run. Speculative rules make reviews noisy.
- It keeps the principles in `plugin/skills/brand-core/SKILL.md`. A change that breaks one needs a decision record first.
- It is tested ([testing.md](testing.md)) and reviewed ([review.md](review.md)).

## Add or change a rule

1. Find the family in `plugin/skills/brand-core/references/rules.md`. A new family is a decision record, not a row.
2. Take the next free number in that family. IDs are never renumbered or reused.
3. Fill every column: severity (MUST, SHOULD or MAY), the assertion, the detect code (S script, J judgment, E render or live search), the remediation and the source.
4. Severity follows the evidence: a palette, type or positioning rule decided by judgment is SHOULD or MAY with status `review`, never MUST.
5. The source is a row in `plugin/research/` (`A<n>`, `C<n>`, `T<n>`, or a named tool from a track B table). New research adds a row there with the date read and, for facts that age, a recheck date. No source means the label `assumption`.
6. A number goes in `references/thresholds.md` with its label, never in a script or a skill.
7. A detect `S` rule gets a check in `brdcheck.py`, a fixture in `plugin/skills/brand-core/tests/fixtures/` and a test case.
8. If the rule needs a new brief field, add it to `references/declaration.md` and `plugin/templates/brief.md`.

## Change a skill or agent

- Shared facts go in `brand-core`; `brand-create` and `brand-review` hold only their own steps. Load reference files at the step that needs them, not up front.
- `SKILL.md` frontmatter: `name` equals the folder name; `description` is at most 1024 characters, written as a folded block (`description: >-`), and says "Use when ...". Keep each `SKILL.md` under 500 lines; move detail into `references/`.
- Output templates live in `plugin/templates/` and are referenced as `${CLAUDE_PLUGIN_ROOT}/templates/<file>`, never embedded.
- Agents return text of at most 300 words. The reviewer stays read-only. Changing an agent's model or effort is a decision record, because the split between designer and reviewer models is deliberate.
- A changed `description` means running the trigger evals by hand ([testing.md](testing.md)).

## Change a script

- Follow `plugin/skills/brand-core/scripts/SPEC.md`: exit codes, the JSON shape, the 40-line summary, `--root`, output only inside `brand/`.
- Standard library only. `fontTools`, `uharfbuzz`, `resvg`, `rsvg-convert` and `svgo` are the optional tools already allowed; anything new needs a decision record.
- Parse SVG as data. Never execute it, render it in a browser or fetch an external reference.

## Versioning

Claude Code updates an installed plugin only when `version` in `plugin/.claude-plugin/plugin.json` rises, so a change without a bump never reaches users. `scripts/check-version.sh` fails a pull request that changes `plugin/` without raising it.

- Patch (0.5.x): wording, a fix, a number in `thresholds.md`, a new source row.
- Minor (0.x.0): a rule, reference, template, script option or agent added; a rule's severity raised.
- Major (x.0.0): a skill renamed or removed, a brief field or a `brand/` file name changed in a way that breaks existing brand folders.
- Files outside `plugin/` (docs, site, examples, CI) need no bump.

Propose the bump with a one-line reason, put it in the same commit as the change, and add a line under `Unreleased` in `CHANGELOG.md`. A release moves those lines under the new version with the date.
