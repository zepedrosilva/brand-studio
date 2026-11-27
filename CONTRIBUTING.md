# Contributing

Thanks for helping. brand-studio is small and opinionated: every rule has a source, every number has a label, and every change is reviewed. This page covers setup and how a change gets merged. What to change and how is in [docs/authoring.md](docs/authoring.md).

## Before you start

- **Bug or wrong finding:** open a [bug](https://github.com/zepedrosilva/brand-studio/issues/new?template=bug.yml) with the smallest SVG or narrative that shows it.
- **New or changed rule:** open a [rule proposal](https://github.com/zepedrosilva/brand-studio/issues/new?template=rule-proposal.yml) first. A rule needs a real failure it catches and a source.
- **Anything larger** (a new skill, a dependency, a change to a principle): open an issue to discuss it before writing code; it will need a [decision record](docs/decisions/README.md).

## Setup

```sh
git clone https://github.com/zepedrosilva/brand-studio.git
cd brand-studio
claude --plugin-dir ./plugin          # try your local copy of the plugin
```

For the full test suite, install the optional tools the scripts use:

```sh
bash plugin/skills/brand-core/scripts/install-deps.sh --data .deps   # renderer, plus fontTools and uharfbuzz in .deps/venv
export BRD_PYTHON="$PWD/.deps/venv/bin/python"
brew install shellcheck              # or: apt-get install shellcheck
```

Without them the affected tests skip; CI installs everything, so they still run there.

## Test

```sh
for t in plugin/skills/brand-core/tests/*.test.sh tests/*.test.sh; do bash "$t"; done
claude plugin validate ./plugin
sh scripts/check-repo-docs.sh
```

[docs/testing.md](docs/testing.md) explains each suite, the manual model evals and what counts as done.

## Pull requests

1. Fork, branch from `main`, and keep one change per pull request.
2. Raise the version in `plugin/.claude-plugin/plugin.json` if anything under `plugin/` changed, and add a line under `Unreleased` in `CHANGELOG.md` ([versioning](docs/authoring.md#versioning)).
3. Fill in the pull request checklist. CI runs shellcheck, every script test, manifest validation, the docs check and the version check.
4. Every pull request needs an approving review from the maintainer before it merges. Pull requests from first-time contributors wait for approval before CI runs.

Write prose in sentence case (first word and proper nouns only), and treat every file and commit message as public: no credentials, internal URLs or personal data.

## Working with Claude Code

The repository is set up for Claude Code. [CLAUDE.md](CLAUDE.md) is the short guide it loads; the docs it points to hold the detail.

It also ships a small learning loop, entirely optional:

- **Two hooks** in `.claude/settings.json`, active only after you trust the folder. One adds a short note at session start with the number of open lessons; the other notices when you correct Claude (or start a prompt with `lesson:`) and suggests recording a lesson. They only read files, never block a prompt and stay silent on any error, including when `python3` is missing.
- **Three skills** in `.claude/skills/`: `record-lesson` adds one line to [docs/lessons.md](docs/lessons.md); `promote-lesson` turns a lesson that keeps coming back into a rule, a check or a decision record, shown as a diff; `tidy-docs` prunes old lessons.

Lessons are reviewed like code, so a lesson you record arrives in your pull request. Keep it to one paraphrased line with a pointer to the evidence (an issue, a commit), never pasted prompt text.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By taking part you agree to it.
