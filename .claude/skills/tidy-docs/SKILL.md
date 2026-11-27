---
name: tidy-docs
description: Prunes lessons and trims CLAUDE.md, each change shown as a diff. Use when scripts/check-repo-docs.sh warns, the session start note says lessons are stale or over the cap, or the user asks to "tidy the docs", "prune lessons" or "trim CLAUDE.md".
---

# Tidy the docs

Run on request or after a warning. Show every change as a diff; apply only after a yes. Edit single lines; never rewrite a whole file.

1. Run `sh scripts/check-repo-docs.sh`. Fix must failures first.
2. Lessons in `docs/lessons.md`:
   - over 15 or older than 90 days: promote with `promote-lesson`, or delete if no longer true;
   - contradicts `CLAUDE.md` or a rule: ask which one holds, with your recommendation and a one-line reason, then keep one;
   - states a trade-off between options: propose a decision record;
   - recurred but never promoted: run `promote-lesson`.
3. `CLAUDE.md` over 150 lines, or holding what the code already shows (file layouts, dependency lists, architecture overviews): delete it or move it to `docs/` or a path rule.
4. Delete any prose rule that a check now enforces; point to the check instead.
5. Fix dead links, update `docs/README.md` if docs changed, and run the check again.
