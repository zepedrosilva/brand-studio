---
name: promote-lesson
description: Promotes a lesson from docs/lessons.md into a check, a path rule, a CLAUDE.md line, a skill or a decision record, shown as a diff and applied only after a yes. Use when a lesson recurred, a promoted rule was broken again, or the user says "promote this lesson" or "make this a rule".
---

# Promote a lesson

Never apply a change before the user says yes to the diff. Ask each question with your recommended answer and a one-line reason, worded so a yes accepts it.

1. Pick the lesson. Promote when it recurred or the user marks it as standing; a one-off waits.
2. Choose the destination: the first test that says yes wins.

   | Test | Destination |
   |---|---|
   | Must hold with zero exceptions and a script can decide | Check: test, lint, CI step or hook |
   | Matters only for part of the tree | Path rule in `.claude/rules/<topic>.md` with `paths` |
   | Needed in nearly every task and not inferable from the code | One line in `CLAUDE.md` |
   | A multi-step procedure | Skill in `.claude/skills/<verb-object>/` |
   | A choice among options with consequences | Decision record in `docs/decisions/` |
   | A personal preference | `CLAUDE.local.md` or auto memory, not the repo |
   | None of these | Leave it until it recurs |

3. Escalate instead of repeating: if the rule already lives on one rung and was broken again, move it one rung up (`CLAUDE.md` line, then path rule, then hook or check). Never add emphasis words.
4. Draft the smallest change and show it as a diff. In the same diff:
   - delete the lesson line from `docs/lessons.md`;
   - leave a back-pointer in the destination as an HTML comment, for example `<!-- from lesson 2026-11-15, PR #12 -->`;
   - if a check now covers a prose rule, delete the prose rule.
5. Apply only after a yes. Then run `sh scripts/check-repo-docs.sh` and fix any must failure you caused.
