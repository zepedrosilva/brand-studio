---
paths:
  - "plugin/skills/brand-core/scripts/**"
  - "plugin/skills/brand-core/tests/**"
---

- Follow `plugin/skills/brand-core/scripts/SPEC.md`: exit codes 0 to 3, the JSON shape, at most 40 summary lines, `--root`, output only inside `brand/`.
- Standard library only; `fontTools`, `uharfbuzz`, `resvg`, `rsvg-convert` and `svgo` are optional and detected at run time. A new dependency needs a decision record.
- SVG is untrusted data: parse it, never execute it, open it in a browser or fetch a reference from it.
- Every fix or new check comes with a fixture and a test case that fails without it.
