# Brief declaration block

Every brand folder carries `brief.md`, filled from `${CLAUDE_PLUGIN_ROOT}/templates/brief.md`. Its declaration block is a fenced `text` block of `key: value` lines under `## Declaration`, so scripts can read it. A missing or thin block is a `brd:DEC-01` finding; reviewers infer what they can and label it as inferred.

| Field | Content | Required | Feeds |
|---|---|---|---|
| `name` | The brand name exactly as written in the wordmark | yes | `brd:DEC-01`, `brd:TYP-01` |
| `concept` | One sentence: the single idea the mark carries | yes | `brd:DEC-01`, `brd:CNC-02` |
| `audience` | Who sees it first, in a few words | yes | `brd:DEC-01` |
| `tone` | 3 to 5 comma-separated tone words | yes | `brd:DEC-01` |
| `avoid` | Things, styles or symbols to avoid, including category clichés | yes | `brd:DEC-01`, `brd:CNC-01` |
| `archetype` | A primary archetype, or `none`; a shortcut into strategy, not a replacement | yes | concept method |
| `metaphor` | The chosen shortlist line, and where the shortlist is (`brief.md#shortlist` by default) | yes | `brd:CNC-01` |
| `wordmark-font` | Family, version, licence (for example `OFL-1.1`), where the licence was read | when a wordmark exists | `brd:TYP-01`, `brd:TYP-02`, `brd:LGL-01` |
| `palette` | One entry per colour: `<name> <#hex> <role>`, roles `background`, `text`, `ui`, `mark`; kept for compatibility and for the master's colours; the full palette is the `## Palette roles` table | after the pick | `brd:CAP-01`, `brd:EVD-02` |
| `positioning` | One line: for `<audience>` who `<need>`, `<name>` is a `<category>` that `<benefit>`; unlike `<main alternative>`, `<difference>` | scope B and C | `brd:POS-01` |
| `own-word` | The one word the brand wants to own in its audience's mind | scope B and C | `brd:POS-01` |
| `assets` | One or two distinctive assets kept unchanged in every file: a colour, a shape or a device | after the pick, scope B and C | `brd:POS-03` |
| `category-colours` | The category's common colours, one entry each: `<name> <#hex> follow\|break: <reason>`, separated by `;` | after the pick, scope B and C | `brd:PAL-07` |
| `pair-cue` | One line naming the non-colour cue that tells apart two colours of equal luminance (a text label, a shape); leave it out when no pair needs one | optional | `brd:EVD-03` |
| `story-status` | `assumed` or `confirmed`: whether the user has confirmed the `## Story` section | when `## Story` is filled | `brd:POS-05` |
| `min-size` | Smallest size the mark is used at, in px | yes | `brd:CRF-02` |
| `grid-unit` | The unit dimensions snap to, in viewBox units | yes | `brd:CRF-03` |
| `tools` | Renderer, optimiser and version, text-to-outline tool, hosted engine or `none` | yes | `brd:EVD-01`, `brd:TYP-04`, `brd:LGL-03` |
| `scope` | `A`, `B` or `C` (see `/brand-create`) | yes | kit steps |
| `jurisdiction` | Where the brand will be used; the legal notes cover the US only | yes | `brd:LGL-01` |

The brief also holds the narrative (as given), the shortlist with clichés, the `## Palette roles`, `## Rationale` and `## Story` sections below, and the `## Waivers` section (format in `severity-and-evidence.md`).

## Palette roles

Filled in kit step 2 (scope B and C). One table; scripts read it, so keep the columns in this order. Method: `colour.md`.

| Column | Content |
|---|---|
| `role` | One of `brand`, `brand-2`, `neutral`, `background`, `text`, `status` |
| `light` | `#RRGGBB` used in light mode |
| `dark` | `#RRGGBB` used in dark mode |
| `ramp` | `<ramp name> <light step>/<dark step>`, steps from 50 (lightest) to 950 (darkest) |

`brand`, `neutral`, `background` and `text` are required (`brd:PAL-01`); `brand-2` is optional and needs a reason in the palette rationale line (`brd:PAL-02`); `status` is only for a brand that ships UI, one row per status colour, told apart by the ramp name (for example `red`, `green`).

## Rationale

Filled in kit steps 2 and 3. One bullet per tone word, then one for the palette and one for the type (`brd:POS-02`). Each line starts with `- `, so scripts never read it as a declaration key.

- `- <tone word>: <how the palette and the type express it>`
- `- palette: <why these roles and hues, from tone and category; never a colour meaning>` (`brd:PAL-05`, `brd:PAL-06`)
- `- type: <family>[ + <family>]. <why it fits; text sizes if stated>` (`brd:TYP-05`, `brd:TYP-06`)

## Story

Filled at kit step 7, after the pick, from the finished brief. One to four short paragraphs separated by a blank line, in three beats: who the brand is for and the tension it answers; the idea and how the mark carries it; how the palette and type follow from it (`brd:POS-05`). Every claim traces to a brief field or a `## Rationale` line, with no colour meanings and no superlatives. Set `story-status: assumed` in the declaration until the user confirms it, then `confirmed`. `brdinuse.py` shows it at the top of `applications.html`; when the section is empty it shows the labelled facts instead.

## Example (invented product, filled after the pick)

```text
name: Tideline
concept: A single wave line that rises and settles: what a log looked like before and after it was read as a timeline.
audience: Backend engineers, who see it first as a repo icon and in the docs header.
tone: calm, exact, quick
avoid: waves with foam, anchors, gears, magnifying glasses, gradients, a bright orange (used by a well-known log tool)
archetype: none
metaphor: one calm wave line that rises and settles (shortlist: brief.md#shortlist, line 4)
wordmark-font: Inter Version 4.0, licence OFL-1.1, read at the family's OFL.txt on 2026-11-19
palette: ink #1B2A34 text; ink #1B2A34 mark; tide-blue #1F6F8B mark; paper #F6F8F9 background
min-size: 16px
grid-unit: 8
story-status: assumed
tools: renderer resvg 0.50.0; optimiser none; text brdtext; hosted engine none
scope: B
jurisdiction: internal and open-source docs; legal notes cover the US only
positioning: for backend engineers who read logs during an incident, Tideline is a log viewer that turns raw lines into a timeline; unlike grep and scrolling, it shows what changed and when
own-word: timeline
assets: the single wave line that rises and settles; tide-blue #1F6F8B as the only brand hue
category-colours: bright orange #F57C00 break: on the avoid list, a well-known log tool owns it; terminal green #33CC66 break: reads as a raw console, the opposite of calm; deep blue #2F6FDB follow: fits the category's technical norm, in a darker, teal-leaning shade
```

```markdown
## Palette roles

| role | light | dark | ramp |
|---|---|---|---|
| brand | #1F6F8B | #5FB3CF | tide 700/300 |
| neutral | #5A6B75 | #9AA9B2 | slate 600/300 |
| background | #F6F8F9 | #10191F | slate 50/950 |
| text | #1B2A34 | #E8EDF0 | slate 900/100 |

## Rationale

- calm: one teal-blue hue on blue-tinted greys, nothing saturated on large areas; the wordmark in sentence case at a medium weight, not in capitals.
- exact: Inter's even, screen-tuned forms; every role pair is measured, not eyeballed; the mark snaps to the 8-unit grid.
- quick: one brand hue and one family, so nothing competes; the one-stroke wave still reads at 16 px.
- palette: tide-blue is the only brand hue, chosen for calm and to follow the category's blue in a darker, teal-leaning shade; the neutrals lean toward it; no claim about what blue means.
- type: Inter. One family for the wordmark and any text, so no second face is needed; body 16 px, smallest 12 px.

## Story

Tideline is a log viewer for backend engineers who read logs during an incident. Raw lines show everything and explain nothing, so it turns them into a timeline of what changed and when.

The mark is one wave line that rises and settles, drawn in a single tide blue, and it still reads at 16 px. The type is Inter at plain sizes, so the lines stay readable.
```

Values the narrative did not give (here audience, the avoid list, `positioning`, `own-word` and `category-colours`) are marked `assumed` in the brief, outside the declaration block. No `brand-2` or `status` rows, so `brd:EVD-03` and `brd:EVD-04` are `n/a` for this brief.
