# Brand brief: brand-studio

Filled by /brand-create step 1. Field meanings: `brand-core/references/declaration.md`. Mark any value the user did not give as `assumed`.

Assumed: none. Audience and positioning confirmed by the user on the live page; own-word "checked" (replacing the suggested "proven", which overclaimed), the vermilion brand colour and the story confirmed in review, 2026-11-27.

## Narrative

`examples/brand-studio/narrative.md` (the plugin's own pitch, agreed with the user on 2026-11-27).

## Essence

- Essence: gives developers without a design background a strong, checked starting brand for their app, so they can get back to building it.
- Tension: branding an app is hard, and asking a model for "an SVG logo" gives circles, gradients and broken letters, with no word on copyright or font licences.
- Tone evidence: careful: "works like a careful designer at your side"; rigorous: "every rule has a number and a source"; honest: "a first draft, not a replacement for a designer"; practical: "get back to building your app".

## Declaration

```text
name: brand-studio
concept: two code brackets holding one finished shape: the developer's world framing the identity you leave with
audience: developers who build apps but have no brand or design background
tone: careful, rigorous, honest, practical
avoid: magic wands and sparkles (the AI cliché), paintbrushes and paint palettes (the design cliché), Bezier pen nibs and handles (the vector-tool cliché), gradients, mascots
archetype: none
metaphor: code angle brackets holding a single solid shape: a developer's world framing one finished mark (concept C, picked 2026-11-27) (shortlist: brief.md#shortlist)
wordmark-font: Space Grotesk Version 2.000 (variable, wght 700), licence OFL-1.1, read at github.com/google/fonts ofl/spacegrotesk/OFL.txt, commit 5026800, 2026-11-27
palette: text #2E2724 mark; brand #D33222 mark; background #FDF3EF background
min-size: 16px
grid-unit: 8
tools: renderer resvg; optimiser none; text brdtext; hosted engine none
scope: C
story-status: confirmed
jurisdiction: worldwide (open-source project); legal notes cover the US only
positioning: for developers who build apps without a design background, brand-studio is a Claude Code plugin that drafts a full brand identity as checked SVG; unlike asking a model for a logo, every mark is checked against numbered, sourced rules before you see it
own-word: checked
assets: the vermilion diamond held inside two ink brackets; the even channel between them
category-colours: violet #7C3AED break: AI tools lean violet and violet-to-blue gradients (assumed); blue #2563EB break: the default colour of developer tools (assumed); multicolour break: design tools often use many hues (assumed)
```

## Shortlist

Clichés in this category: magic wand and sparkles (AI tools), paintbrush or paint palette (design tools), pen nib with Bezier handles (vector editors).

Scores: concept, distinct, primitives, 16 px (0 to 2 each), name test (0 to 4, counts double), total 0 to 12.

| # | One-liner | Literal or abstract | Score (0-12) | Chosen |
|---|---|---|---|---|
| 1 | A drafting compass mid-arc: the instrument of careful construction, drawing the one circle everything is built on. | literal | 2+2+2+1+3 = 10 | a |
| 2 | The end of a branding iron, a simple geometric seal: the oldest meaning of "brand", a mark made once and made to last. | literal | 2+2+2+2+3 = 11 | b |
| 3 | Code angle brackets holding a single solid shape: a developer's world framing one finished mark. | literal | 2+2+2+2+2 = 10 | c |
| 4 | A set square with a circle resting on it: drafting tools as proof of construction. | literal | 2+1+2+1+2 = 8 | |
| 5 | An easel holding one blank square canvas: the studio waiting for the app's idea. | literal | 1+1+2+1+3 = 8 | |
| 6 | Three tiles, one raised: three concepts and a single pick. | abstract | 2+2+2+2+1 = 9 | |
| 7 | A check mark emerging from construction circles: a mark proven before it is shown. | abstract | 2+1+2+2+1 = 8 | |
| 8 | A grid with one filled cell growing into a shape: an identity built on a unit. | abstract | 1+2+2+1+1 = 7 | |
| 9 | A seal stamp pressing a square: approved, signed off. | literal | 1+1+2+2+2 = 8 | |
| 10 | Sparkles around a square (the AI cliché, no twist). | abstract | 0+0+2+1+1 = 4 | |

Chosen lines (distinct ideas, all three literal with a name test of 2 or more): a (compass: construction), b (branding iron: the word "brand"), c (brackets: the developer's world).

## Palette roles

Filled in kit step 2. `brand-2` is optional; `status` rows only for a brand that ships UI. Method: `brand-core/references/colour.md`.

| role | light | dark | ramp |
|---|---|---|---|
| brand | #D33222 | #FE5F4B | vermilion 600/400 |
| neutral | #766E6A | #A59C98 | stone 600/400 |
| background | #FDF3EF | #1B1412 | stone 50/950 |
| text | #2E2724 | #FDF3EF | stone 900/50 |

Ramps (OKLCH, lightness steps 50 to 950 at 0.97 to 0.20; chroma reduced only to stay in sRGB): vermilion hue 30, chroma 0.20, with the light value solved at L 0.569 (4.53:1) and the dark at L 0.690 (6.02:1); the first pick, ember (hue 38, chroma 0.17, #BF4213), was replaced at review because it read brown; stone hue 45, chroma 0.012 (a neutral leaning toward the brand hue); the light neutral sits at L 0.545, between steps 500 and 600, so it clears 4.5:1 on the background (brd:EVD-02).

## Rationale

Filled in kit steps 2 and 3: one line per tone word, then palette and type. Never a colour meaning.

- careful: one accent only, used on one shape, so colour is never decoration; one type family, one weight in the wordmark.
- rigorous: every value comes from two OKLCH ramps with measured contrast; letters are shaped, kerned outlines, not drawn.
- honest: a plain warm neutral and near-black ink, no gradients or glow; lowercase, the name written as it is typed.
- practical: four roles, each with a light and a dark value, ready to drop into an app; a grotesque that reads at small sizes on screen.
- palette: breaks the category's violet and blue so the mark stands apart from AI and developer tools; a warm neutral keeps the accent the only saturated colour.
- type: Space Grotesk. A grotesque with technical details that sits beside code without looking like a code font; bold lowercase for the wordmark, matching the mark's weight. Text sizes not stated.

## Story

Most developers can build an app but have never designed an identity for one. Ask a model for a logo and you get circles, gradients and broken letters, with no word about who owns them.

brand-studio works the way a careful designer does: one idea, three concepts drawn in black, each checked and rendered before you see it, one pick, and a kit built by editing that pick. Every rule it applies has a number and a source.

The mark is a pair of code brackets holding one finished shape: the developer's world, framing the identity you leave with. The shape carries the only colour; the rest is ink, and a lowercase wordmark that sits comfortably next to code.

## Waivers

<!-- Waives brd:<ID> for <file>: <reason>. Owner: <name>. Review by: <date>. -->
