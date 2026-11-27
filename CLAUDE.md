# Project guide

Guidance for Claude Code in this repo. Keep it short: only what Claude cannot work out from the code. Cap: 200 lines.

## Purpose

`brand-studio`, a Claude Code plugin that turns a narrative into a first-draft brand identity as SVG and reviews SVG logos against numbered `brd:` rules. For developers without a brand or design background who need a strong starting identity for an app, so they can spend their time on the app itself. A first draft, not a replacement for a designer.

The repository is public. Treat every file as public: no credentials, internal URLs, company names or personal data in any file, commit message or lesson.

## Layout

- `plugin/` is what users install (manifest, skills, agents, templates, research). Everything else is the project around it: docs, examples, site, CI. The site is published by the catalog repo, which runs `scripts/build-site.sh`; this repo has no Pages workflow. Never make the plugin read a file outside `plugin/`.
- The plugin is listed in a separate catalog repository (`zepedrosilva/plugins`); this repo has no `marketplace.json`.

## Commands

- Build: none
- Test: `for t in plugin/skills/brand-core/tests/*.test.sh; do bash "$t"; done && claude plugin validate ./plugin`
- Try the plugin locally: `claude --plugin-dir ./plugin`
- Check these docs: `sh scripts/check-repo-docs.sh`
- Check the version bump: `sh scripts/check-version.sh origin/main`

## Rules

- Raise `version` in `plugin/.claude-plugin/plugin.json` whenever a file under `plugin/` changes, except documentation-only `plugin/research/`; installed copies update only then. Propose the bump with a reason and wait for a yes. See [docs/authoring.md](docs/authoring.md).
- Rule IDs (`brd:CRF-02`) are permanent: never renumber or reuse one.
- Every rule and threshold cites a source from `plugin/research/` (an `A<n>`, `C<n>` or `T<n>` row, or a named tool from its track B table) or is labelled `assumption`.
- Sentence capitalisation in all prose: first word and proper nouns only.

## Where to look

- [docs/README.md](docs/README.md): index of the docs
- [docs/context.md](docs/context.md): glossary; use these terms
- [docs/architecture.md](docs/architecture.md): structure and boundaries
- [docs/authoring.md](docs/authoring.md): change a rule, skill, agent or script; versioning
- [docs/testing.md](docs/testing.md): how to test
- [docs/review.md](docs/review.md): how to review a change
- [docs/decisions/README.md](docs/decisions/README.md): decisions and why
- [docs/lessons.md](docs/lessons.md): lessons not yet promoted
- [docs/open-questions.md](docs/open-questions.md): unresolved questions
- `.claude/rules/`: rules that load only for matching paths

## Questions

- Every question you ask the user carries your recommended answer and a one-line reason, worded so a yes accepts it.

## Lessons

- After the user corrects you, or you find a project fact you could not have inferred, run the `record-lesson` skill. A prompt that starts with `lesson:` is always a lesson.
- Record a paraphrased rule and a pointer to the evidence. Never copy prompt text into a file.
- A lesson that recurs is promoted with the `promote-lesson` skill: shown as a diff, applied only after a yes.
- If a promoted rule is broken again, move it one rung up (path rule, then hook or check). Do not add emphasis.

## Memory

- Team facts live in this repo: lessons, rules, decisions.
- Personal preferences go in `CLAUDE.local.md` (not committed) or auto memory.
- When this file and auto memory disagree, this file wins.
