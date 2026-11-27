---
paths:
  - "plugin/skills/**/SKILL.md"
  - "plugin/skills/**/references/*.md"
  - "plugin/agents/*.md"
---

- Rule IDs are permanent: add new ones at the next free number in their family; never renumber or reuse one.
- Every rule and number cites a source from `plugin/research/` or is labelled `assumption`; numbers live only in `references/thresholds.md`.
- A judgment-only palette, type or positioning rule is SHOULD or MAY, never MUST.
- Shared facts live in `brand-core`; do not copy them into `brand-create` or `brand-review`.
- Any change here raises the plugin version (`docs/authoring.md`).
