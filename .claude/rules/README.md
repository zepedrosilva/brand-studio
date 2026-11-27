<!--
Path rules for Claude Code.

Each rule is a markdown file in this folder. A rule with a `paths` list in its frontmatter
loads when Claude works with a matching file. A rule without `paths` loads in every session,
like CLAUDE.md, so prefer scoped rules. Keep this README short for the same reason.
Quote each glob. scripts/check-repo-docs.sh checks the frontmatter (LOC-04).

Example, saved as .claude/rules/api.md:

---
paths:
  - "src/api/**"
---

- Validate every request body at the handler; never trust client input.
-->
