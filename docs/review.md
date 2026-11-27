# Review

What a reviewer checks before a change is merged, human or agent. Keep only what a check script cannot catch. Mark each finding blocking or non-blocking, with `path:line`.

## Every change

- Public: no credentials, internal URLs, company names or personal data in the diff, the commit messages or a lesson.
- Need: the change answers a real observed failure or request (link the issue), not a speculative one.
- Version: raised per [authoring.md](authoring.md) when `plugin/` changed, and the bump matches the change.
- Changelog: an `Unreleased` line for any user-visible change.

## A rule change

- The ID is new and never reused; an existing rule is never renumbered.
- Severity matches the evidence: a rule decided by judgment on palette, type or positioning is SHOULD or MAY, never MUST.
- The source column cites a row in `plugin/research/` or says `assumption`; a new source adds a row there with its date.
- A script-checkable rule (detect `S`) comes with a fixture and a test.
- The reviewer and the designer can both act on it: the fix column says what to do.

## A skill or agent change

- A changed `description` is specific, has a "Use when" phrase, and does not overlap the other skills; trigger evals were run by hand ([testing.md](testing.md)).
- Facts shared by both workflows stay in `brand-core`; nothing is copied into a workflow.
- The reviewer stays read-only and blind at the concept review ([architecture.md](architecture.md)).
- A workflow change was tried end to end once, and the pull request says so.

## A script change

- Standard library only, apart from the optional tools already listed; a new dependency needs a decision record.
- SVG is still parsed as data, never executed or fetched; output stays inside `brand/`.
- Exit codes and the JSON shape follow `plugin/skills/brand-core/scripts/SPEC.md`; numbers come from `thresholds.md`.
