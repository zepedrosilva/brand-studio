# Lessons

Short rules learned from real corrections, not yet promoted. Add with the `record-lesson` skill; promote recurring ones with `promote-lesson`, then delete them here. Keep at most 15.

Format, one line per lesson: `- YYYY-MM-DD · <evidence pointer> · <rule, paraphrased> · promote-to: <CLAUDE.md|rule|adr|check|skill|none>`

Evidence is a pointer (PR, issue, commit, ADR, file path or "session"), never quoted prompt text.

<!--
- 2026-01-31 · PR #12 · Run the migration check before changing a schema · promote-to: check
-->
- 2026-11-27 · session (install-deps e2e run) · Put any command that needs ${CLAUDE_PLUGIN_ROOT} or ${CLAUDE_PLUGIN_DATA} in a skill the Skill tool loads or in an agent, since files read from brand-core or references keep the placeholder unfilled · promote-to: rule
