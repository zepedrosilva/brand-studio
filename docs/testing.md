# Testing

How to test a change: which tests to run, what they need, and what counts as done.

## Commands

- Script tests: `for t in plugin/skills/brand-core/tests/*.test.sh; do bash "$t"; done`. Each suite prints what it skipped.
- Manifest: `claude plugin validate ./plugin`.
- Version bump: `sh scripts/check-version.sh origin/main` fails when `plugin/` changed and the version did not rise.
- Repo docs, lessons, hooks and secrets: `sh scripts/check-repo-docs.sh`.
- Shell lint: `shellcheck plugin/skills/*/tests/*.test.sh scripts/*.sh`.

## What the script tests need

- Python 3. Set `BRD_PYTHON` to use a specific interpreter (CI points it at a venv).
- `brdtext` tests need `fontTools` and `uharfbuzz` (`bash plugin/skills/brand-core/scripts/install-deps.sh --data .deps`, then `BRD_PYTHON=.deps/venv/bin/python`); without them those cases skip.
- `brdrender` has two layers: a fake renderer in `fixtures/bin/resvg` that always runs, and a real-renderer test that runs when `resvg` or `rsvg-convert` is installed.
- Fixtures live in `plugin/skills/brand-core/tests/fixtures/`. A bug fix in a script comes with a fixture and a test that fails without the fix.

CI installs every optional tool, so a skip locally is not a skip in CI.

## Manual: model evals

`plugin/skills/brand-create/tests/evals.json` and `plugin/skills/brand-review/tests/evals.json` hold trigger-accuracy prompts: requests that should and should not start each skill. They are run by hand, not in CI, because they cost model calls and are not deterministic. Run them when a skill's `description` changes: start `claude --plugin-dir ./plugin`, send each prompt in a fresh session, and check that the skill triggered (or did not) as `expect_trigger` says. Note the result in the pull request.

## Manual: an end-to-end run

A change to a workflow step, an agent or a template needs one real run of `/brand-studio:brand-create` on a short narrative, with an image-capable model, through the checkpoint to the final brief. Say in the pull request what you ran and what the final verdict was.

## Done means

- Every script suite passes in CI, with no new skips.
- `claude plugin validate ./plugin` passes.
- The version rose if `plugin/` changed.
- Manual evals or an end-to-end run, when the change calls for them, are reported in the pull request.
