## What and why

<!-- One or two sentences, and the issue it closes. -->

## Checklist

- [ ] Tests pass locally (`docs/testing.md`), and a script fix comes with a test that fails without it
- [ ] Version raised in `plugin/.claude-plugin/plugin.json` if anything under `plugin/` changed (`docs/authoring.md`)
- [ ] A line under `Unreleased` in `CHANGELOG.md` for a user-visible change
- [ ] New or changed rules cite a source in `plugin/research/` or are labelled `assumption`
- [ ] Trigger evals run by hand if a skill `description` changed; an end-to-end run if a workflow step changed (say what you ran)
- [ ] Nothing private: no credentials, internal URLs, company names or personal data
