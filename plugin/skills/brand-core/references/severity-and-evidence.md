# Severity, verdicts and evidence

Applies to every `brd` rule and every review, whether run by `/brand-review`, the `brand-reviewer` agent or a designer's self-check.

## Severity

| Severity | Effect |
|---|---|
| MUST | An unwaived failure fails the review. An unresolved MUST (`review` or `not run`) makes the review `incomplete`. |
| SHOULD | A finding; fix it or justify it in the brief. |
| MAY | A note. |
| MUST (warn) and all LGL rules | Never pass or fail. Always reported in the legal warning block. Not waivable, because they do not block. |

## Status of a finding

| Status | Meaning |
|---|---|
| `pass` | The rule was checked and holds. |
| `fail` | The rule was checked and does not hold. |
| `review` | A script or a check could not decide; a person or the reviewer must confirm or dismiss it in one line. |
| `waived` | A waiver line in the brief names this rule and file. |
| `warn` | LGL rules only. |
| `not run` | The input or a tool was missing; say which. |
| `n/a` | The rule has nothing to check here (see Applicability). Never counted in the verdict. |

## Applicability

A rule that has nothing to check is `n/a`. It is left out of the verdict and named in `Scope`, so a review of one bare SVG can still end `pass`.

| Rule | Applies only when |
|---|---|
| `brd:DEC-01`, `brd:CNC-*` | a `brief.md` exists (no brief: `n/a`) |
| `brd:TYP-01` font record, `brd:TYP-02`, `brd:TYP-03`, `brd:TYP-04` | a wordmark or lockup exists; with no brief, ask once where the font is recorded, and leave it `review` if nobody can say |
| `brd:SET-*` | an icon set (`icons/`) is in scope |
| `brd:EVD-02` | a brief with a `palette` line or a `## Palette roles` table exists (neither: `n/a`) |
| `brd:PAL-*` | the brief has a `## Palette roles` table (none: `n/a`); this includes `brd:PAL-08` and `brd:PAL-09` |
| `brd:CTR-06` | every final kit (the last review of scope A, B or C); a missing or incomplete export set is a MUST failure and the verdict is `fail`. With no renderer installed, the PNGs are `not run` and the verdict is `incomplete`, with installing `resvg` or `rsvg-convert` as the next step. Concepts at the checkpoint and a single SVG under review: `n/a` |
| `brd:EVD-03`, `brd:EVD-04` | the brief has a `## Palette roles` table with a pair to compare: a `brand-2` row, or two `status` rows (none: `n/a`) |
| `brd:POS-*` | the brief has a positioning field: `positioning`, `own-word`, `assets`, `category-colours`, a `## Rationale` section or a `## Story` section (none: `n/a`) |
| `brd:TYP-05`, `brd:TYP-06`, `brd:TYP-08` | the brief has a `## Rationale` section, or the brand sheet states type (neither: `n/a`) |
| `brd:TYP-07` | a wordmark or lockup exists |

The live-text half of `brd:TYP-01` (any `<text>`) applies to every file. All other MUST rules except `brd:CTR-06` (a folder rule) apply to every SVG.

A render rule (detect E) checked without any render is `review`, never `pass`. A finding cites every rule the defect breaks, on one line (for example live text in a master breaks `brd:CTR-04` and `brd:TYP-01`); each check has one owning rule, named in `rules.md`.

## Evidence levels

Every finding names the level its verdict rests on. The detect code in the catalogue is the best level possible; report the level actually used.

| Level | Means | Confidence |
|---|---|---|
| `script` | `brdcheck.py` or `brdtext.py` decided it | highest; deterministic |
| `render` | A raster of the final file was looked at (`brdrender.py` or another renderer) | high for visual rules |
| `judgment` | Reasoning from the SVG text, the brief or the conversation | lowest |

Raster input (PNG, JPG) to a review: every finding is `judgment` from a vision-only reading; the script rules (`brd:CTR-*`, `brd:CAP-01`, `brd:CAP-03`, `brd:CRF-03`, `brd:SET-*`, `brd:SEC-01`) are `not run`; the verdict is marked `provisional (raster input)`. Ask for the SVG for a full review. Tracing a raster is out of scope in v1.

## Source labels

Separate from evidence levels: a source label says how much weight the rule or number itself carries, not how a finding was decided. Every catalogue row that cites `research/brd-colour-type-research.md`, and every number in `thresholds.md`, carries one.

| Label | Means |
|---|---|
| standard | A published standard, read during research (for example WCAG 2.2) |
| vendor guidance | A platform or design-system vendor's published guidance; not a standard |
| practitioner opinion | Repeated by practitioners or popular skills; not authoritative; tune to your case |
| weak or contested evidence | Widely repeated, but studies do not support it or disagree; never a reason on its own |
| research (strength stated) | A peer-reviewed finding; the label names its strength (for example "moderate, lab ratings of colour pairs") and its limits |

`verify before release` and `assumption` mark numbers in `thresholds.md` (definitions there). A palette, type or positioning rule decided by judgment is SHOULD or MAY with status `review`, never MUST.

## Verdict

Apply the first row that matches:

| Verdict | When |
|---|---|
| `fail` | Any MUST is `fail` and not waived. |
| `incomplete` | No MUST fails, but at least one MUST is `review` or `not run`. Never reported as a pass. |
| `pass with findings` | Every applicable MUST is `pass` or `waived`; SHOULD or MAY findings, or SHOULD `review` items, remain. |
| `pass` | Every applicable rule is `pass` or `waived`. |

An `incomplete` verdict lists, for each unresolved MUST, the exact next step that resolves it. The usual case is no renderer, which leaves `brd:CRF-01` and `brd:CRF-02` (and SHOULD `brd:CAP-02`) in `review`:

```
Verdict: incomplete
Unresolved MUST:
- review brd:CRF-02 mark.svg: legibility at 16, 32, 64 px not seen on a render; the 2-unit gap is below 1/48 of the mark and may close at 16 px [evidence: judgment]
  Next step: install resvg or rsvg-convert, run
  python3 ${CLAUDE_PLUGIN_ROOT}/skills/brand-core/scripts/brdrender.py mark.svg --out brand/renders
  then re-run /brand-review. Without a renderer the verdict stays incomplete.
```

The legal warning block is appended to every verdict, whatever the result.

## Finding line

```
<status> brd:<ID>[, brd:<ID>] <file>: <finding> -> <fix> [evidence: script|render|judgment]
```

## Waivers

A waiver is one line in the `## Waivers` section of `brief.md`:

```
Waives brd:<ID> for <file>: <reason>. Owner: <name>. Review by: <date>.
```

Scripts honour waivers that name the exact rule and file. An expired review date turns the waiver back into a finding.

## Legal warning block

Appended to every review and to the brand sheet:

```
Legal warnings (not legal advice; US-centred, other jurisdictions not researched)
- brd:LGL-01 <present | missing> in brand-sheet.md
- brd:LGL-02 <resemblances noticed, or "none noticed; run the searches in legal.md">
- brd:LGL-03 <hosted engine and terms, or "no hosted engine used">
- brd:LGL-04 <provenance note present | missing>
```
