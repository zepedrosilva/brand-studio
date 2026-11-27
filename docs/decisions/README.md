# Decisions

Decision records (ADRs): one file per decision that had real alternatives and consequences.

- Copy `0000-template.md` to `NNNN-title-with-dashes.md` with the next free number. Numbers are never reused.
- Status is one of `proposed`, `accepted`, `rejected`, `deprecated` or `superseded by NNNN`.
- When a decision changes, write a new record and mark the old one superseded. Do not edit the old body.
- Keep a record under about 80 lines.

| Number | Title | Status |
|---|---|---|
| [0001](0001-greyscale-primitives-first-concepts.md) | Concepts are drawn greyscale, primitives first | accepted |
| [0002](0002-wordmarks-from-outlined-open-fonts.md) | Wordmarks are outlined from OFL or Apache fonts | accepted |
| [0003](0003-one-checkpoint-then-edit.md) | One checkpoint, then edit rather than regenerate | accepted |
| [0004](0004-separate-designer-and-reviewer-models.md) | Designer and reviewer are separate agents on different models | accepted |
| [0005](0005-optional-standard-library-scripts.md) | Scripts are optional and use the standard library | accepted |
| [0006](0006-static-svg-1-1-masters.md) | Masters are static SVG 1.1 | accepted |
| [0007](0007-legal-warnings-only-us-centred.md) | Legal items are warnings, US-centred | accepted |
| [0008](0008-no-hosted-generator.md) | No hosted image or vector generator | accepted |
| [0009](0009-ask-to-install-then-degrade.md) | Ask to install missing tools, degrade only when the user declines | accepted |
