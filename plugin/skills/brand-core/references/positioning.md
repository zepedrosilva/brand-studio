# Positioning: statement, word to own, assets and rationale

Loaded at brief step 1 (positioning fields), kit steps 2 and 3 (rationale lines, assets) and by reviews of a brief with positioning fields. Rules: `brd:POS-01` to `brd:POS-04`, `brd:PAL-07`; fields: `declaration.md`. Sources cite `research/brd-colour-type-research.md` (`C<n>`, `T<n>`), paraphrased. The positioning books below were read only through secondary comparisons, so every claim from them is practitioner opinion.

How colour and type express positioning is weakly supported (colour.md, "What the evidence supports"; type.md), so the kit asks for a stated rationale, never a lookup table.

## When to fill what

| Field | When | Rule |
|---|---|---|
| `positioning`, `own-word` | Brief step 1, asked once with suggested values; unanswered ones are marked `assumed` | `brd:POS-01` |
| `category-colours` | Kit step 2, before choosing roles | `brd:PAL-07` |
| `## Rationale` palette and tone lines | Kit step 2 | `brd:POS-02` |
| `## Rationale` type line, tone lines completed | Kit step 3 | `brd:POS-02`, `brd:TYP-05` |
| `assets` | After the pick, once the mark and brand colour exist | `brd:POS-03` |

## The statement (`brd:POS-01`)

One line, from the short fill-in template that compares against an alternative (Moore, via C47; practitioner opinion):

```text
for <audience> who <need>, <name> is a <category> that <benefit>; unlike <main alternative>, <difference>
```

Checks, the kit's own (assumption):

- The audience matches the brief's `audience`, and the need comes from the narrative's tension.
- The category is one the audience would use to describe it.
- The main alternative is real: a competitor, a habit or doing nothing.
- The difference is something the alternative cannot also claim; no superlative without proof.

A longer, evidence-first process exists (Dunford, via C47), starting from competitive alternatives and value; it is heavier than this kit's audience needs. Offer it only if the user asks.

## The word to own

Positioning works on the audience's mind; aim to own one word or position (Ries and Trout, via C47; practitioner opinion). Test the `own-word`: a strong alternative should not already own it, and it should appear in, or be implied by, the statement. Example from the Tideline brief: `timeline`.

## Distinctive assets (`brd:POS-03`)

An asset helps recognition when it is both well known and unique to the brand, and it becomes so through consistent use (Sharp and Romaniuk, via secondary pages, C50; practitioner opinion with research behind it). Colour alone is a weak asset, because categories share palettes (C50, secondary claim).

- Name one or two: usually the brand colour together with a shape or device from the mark.
- Keep them unchanged in every file and use; a changed font or case of a known name slows recognition (C29; research, moderate to weak).

## From tone words to palette and type (`brd:POS-02`)

Write one line per tone word naming the concrete choice that expresses it. Use these levers, which the research ties to impressions more firmly than hue is tied to meaning; they are prompts, not answers.

| Lever | What to decide | Evidence |
|---|---|---|
| Lightness and saturation | How light, how saturated, on how much area | Stronger than hue in lab ratings (C20; research, moderate) |
| Number of hues | One brand hue, or a second with a job | practitioner opinion (T2, T5, C39) |
| Lightness contrast | Quiet or sharp contrast between brand and neutral | Pair preference rises with lightness contrast (C18; research, moderate) |
| Construction | Serif or sans, geometric or humanist | Six typeface dimensions predict impressions (C27; research, moderate) |
| Weight | Light, regular or heavy | Weight trades prominence against other impressions (C27) |
| Case | Lowercase, sentence case or capitals | C29; research, moderate to weak |
| Elaborateness | Plain or detailed | Recognised logos are natural and moderately elaborate (C26; research, moderate) |

Never assign a hue to a tone word by meaning (`brd:PAL-06`). "Calm" may become "one low-chroma hue on tinted greys"; it never becomes "blue, because blue is calm".

## Clichés

`brd:CNC-01` already names the category's symbol clichés. Extend the same habit to colour and type: name the category's usual colours in `category-colours` and its usual typefaces in the type line, then follow or break each with a reason (T5, name the generic defaults and then choose deliberately; practitioner opinion). Do not copy another skill's list of fonts or colours to avoid: such lists track fashion.

## Archetypes and personality labels (`brd:POS-04`)

- The five brand-personality dimensions (sincerity, excitement, competence, sophistication, ruggedness) describe how people perceive a brand; they do not prescribe colours (Aaker 1997, C48; research, moderate).
- The twelve brand archetypes come from a 2001 marketing book rather than from Jung, and independent validation is scarce (C49; weak or contested evidence).
- Either may be recorded in `archetype` as a storytelling aid. Neither is the reason for a colour or a typeface.

## The story (`brd:POS-05`)

A short story gives the finished kit a reason to be looked at: it opens `applications.html` and the brand sheet. It is drafted from the finished brief at kit step 7 and is the only prose in the kit, so it is held to the brief.

- **Three beats.** Who the brand is for and the tension it answers; the idea and how the mark carries it; how the palette and type follow from it. One to four short paragraphs.
- **Traceable.** Each sentence comes from a brief field (`audience`, the essence tension, `concept`, `metaphor`, `assets`) or a `## Rationale` line. A fact the brief does not give is left out, not invented.
- **No colour meanings, no superlatives.** The palette line follows `colour.md`: say what a choice does (restraint, readability), never what a colour "means".
- **A draft until confirmed.** `story-status: assumed` shows a draft note on the page; `confirmed` removes it.

## On the brand sheet

The one-page minimum (logo files, colour codes, font names, clear space, minimum size) is already in the sheet (C51; practitioner opinion). The positioning section adds the statement, the word to own, the distinctive assets and the category-colour choices, and the story opens the sheet.
