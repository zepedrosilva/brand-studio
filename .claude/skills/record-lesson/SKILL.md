---
name: record-lesson
description: Records one lesson in docs/lessons.md after a correction or a newly found project fact. Use when the user corrects Claude, starts a prompt with "lesson:", says "remember this next time" or "you did that again", or a hook note says a prompt may be a correction.
---

# Record a lesson

Appending one line to `docs/lessons.md` is the only change this skill makes on its own.

1. Decide if it is a lesson: would it apply again in this repo? A clarification of the current task is not a lesson. A personal preference goes to `CLAUDE.local.md` or auto memory instead.
2. Search first: grep `CLAUDE.md`, `.claude/rules/` and `docs/lessons.md` for the same subject.
   - A similar lesson exists: it recurred. Do not add a duplicate; run the `promote-lesson` skill.
   - A promoted rule already covers it: the rule was broken again. Run `promote-lesson` to move it one rung up.
   - It contradicts an existing line: the existing line wins until the user says otherwise. Ask.
3. Append one line:
   `- YYYY-MM-DD · <evidence pointer> · <rule, paraphrased> · promote-to: <CLAUDE.md|rule|adr|check|skill|none>`
   - Evidence is a pointer: PR, issue, commit, ADR, file path, or `session`. Never quote the user, never paste prompt text, secrets or links to internal hosts.
   - The rule is one plain sentence in the imperative. No emphasis words.
   - `promote-to` is your best guess using the ladder in `promote-lesson`; `none` if unsure.
4. Tell the user in one line what you recorded and where.
