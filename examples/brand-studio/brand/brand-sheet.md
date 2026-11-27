# brand-studio: brand sheet

First-draft identity made with brand-studio on 2026-11-27. A strong draft, not a professional identity; review it with a designer before wide use.

## Story

Most developers can build an app but have never designed an identity for one. Ask a model for a logo and you get circles, gradients and broken letters, with no word about who owns them.

brand-studio works the way a careful designer does: one idea, three concepts drawn in black, each checked and rendered before you see it, one pick, and a kit built by editing that pick. Every rule it applies has a number and a source.

The mark is a pair of code brackets holding one finished shape: the developer's world, framing the identity you leave with. The shape carries the only colour; the rest is ink, and a lowercase wordmark that sits comfortably next to code.

## Concept

Two code brackets holding one finished shape: the developer's world framing the identity you leave with. The brackets run at 45 degrees and face inward around one solid diamond, built from three polygons on an 8-unit grid; the diamond's edges run parallel to the brackets, so the channel between them is the same width all round.

## Positioning

- Statement: for developers who build apps without a design background, brand-studio is a Claude Code plugin that drafts a full brand identity as checked SVG; unlike asking a model for a logo, every mark is checked against numbered, sourced rules before you see it (brd:POS-01)
- Word to own: checked. The one word people should connect with the brand without being told; it steers the rationale and the copy
- Distinctive assets: the vermilion diamond held inside two ink brackets, and the even channel between them; keep them unchanged in every file and every use (brd:POS-03)
- Category colours: violet breaks (AI tools lean violet and violet-to-blue gradients); blue breaks (the default of developer tools); multicolour breaks (design tools). All three observations are assumed, not surveyed (brd:PAL-07)

## Files

| File | Use |
|---|---|
| `mark.svg` | Master, flat colours |
| `mark-mono.svg` | One colour |
| `mark-reversed.svg` | On dark backgrounds |
| `wordmark.svg` | Outlined name |
| `lockup-horizontal.svg` | Mark and name side by side |
| `lockup-stacked.svg` | Mark above name |
| `*-reversed.svg` | Wordmark and lockups for dark backgrounds |
| `favicon.svg` | Browser tab |
| `app-icon.svg`, `app-icon-dark.svg` | 1024 px square app icon, light and dark, no pre-rounded corners |
| `social.svg` | 1200 by 630 social image: the horizontal lockup on the background colour |
| `icons/` | Six interface icons and `style-spec.json` |

## Downloads (brd:CTR-06)

- Everything in one file: `exports/brand-studio-brand-assets.zip`
- Vector: `exports/svg/` (one SVG per file above)
- Raster: `exports/png/`, each file at 16, 32, 48, 64, 128, 256, 512 and 1024 px
- Applications: `applications.html` shows the kit in a phone app, a browser tab, an app icon, a web page, a dark card, a slide and a flyer, with every colour pair measured
- Transparency: every PNG has a transparent background, so it sits on any colour; only tiles (`app-icon*`, `social*`, `favicon*`, `*-tile*`) carry their own background. Use the reversed files on dark backgrounds.

## Palette

| Name | Hex | Role | Contrast against background (brd:EVD-02) |
|---|---|---|---|
| text | #2E2724 | mark (brackets) | 13.44:1 |
| brand | #D33222 | mark (diamond) | 4.53:1 |
| background | #FDF3EF | background | n/a |

### Palette roles

| Role | Light | Dark | Ramp | Contrast on background, light / dark (brd:EVD-02) |
|---|---|---|---|---|
| brand | #D33222 | #FE5F4B | vermilion 600/400 | 4.53:1 / 6.02:1 |
| neutral | #766E6A | #A59C98 | stone 600/400 | 4.57:1 / 6.76:1 |
| background | #FDF3EF | #1B1412 | stone 50/950 | n/a |
| text | #2E2724 | #FDF3EF | stone 900/50 | 13.44:1 / 16.65:1 |

Ramps are built in OKLCH: vermilion at hue 30 and chroma 0.20, stone at hue 45 and chroma 0.012, so the neutral leans toward the brand hue. The brand values are solved at the lightest point that clears 4.5:1, so the colour is as bright as the contrast floor allows. A first pick, a darker burnt orange, was replaced at review because it read brown. The light neutral sits at lightness 0.545, between two ramp steps, because the step above it measured 4.44:1 and ratios are never rounded up.

Colour-blind check (brd:EVD-03, brd:EVD-04): n/a. There is no `brand-2` and no `status` rows, so no pair has to be told apart by colour alone; the brackets and the diamond also differ by 13.44:1 against 4.53:1 in lightness and by shape.

| Pair | Contrast between them | Deutan | Protan | Tritan (review) |
|---|---|---|---|---|
| n/a | n/a | n/a | n/a | n/a |

Why this palette: breaks the category's violet and blue so the mark stands apart from AI and developer tools; a warm neutral keeps the accent the only saturated colour.

Dark set: `mark-reversed.svg`, `wordmark-reversed.svg`, both reversed lockups and `app-icon-dark.svg`, all in the dark role values.

## Typography

Space Grotesk Version 2.000 (variable font, weight 700), OFL-1.1, licence read at github.com/google/fonts `ofl/spacegrotesk/OFL.txt`, commit 5026800, on 2026-11-27. The wordmark is outlined; the font is not needed to display it.

- Families: one, Space Grotesk (brd:TYP-05)
- Text sizes: none stated (brd:TYP-06)
- Why this type: a grotesque with technical details that sits beside code without looking like a code font; bold lowercase for the wordmark, matching the mark's weight. Careful: one family, one weight. Rigorous: shaped, kerned outlines, not drawn letters. Honest: lowercase, the name written as it is typed. Practical: reads at small sizes on screen.

## Clear space and minimum size

- Clear space: one bracket width (the horizontal thickness of a bracket arm, 40 of the mark's 256 units) on every side.
- Minimum size: mark 16 px; horizontal lockup 120 px wide; stacked lockup 80 px wide. The lockup minimums are an assumption from the renders, not a measured rule.

## Misuse

- Do not stretch, rotate, recolour outside the palette, add effects or outline the mark.
- Do not set the name in live text in place of the wordmark.
- Do not place the full-colour mark on a background that fails the contrast table; use the mono or reversed file.
- Do not swap the colours of the brackets and the diamond: the diamond is the only accent.

## Evidence

Checks run: brdcheck 0.1.0, brdrender 0.1.0 with resvg 0.50.0, brdtext 0.1.0 with fontTools 4.68.0 and uharfbuzz 0.57.0, brdinuse 0.1.0. On `social.svg`, the anchor count (brd:CAP-03) and grid (brd:CRF-03) items come from the outlined letters, which the script exempts only in files named `wordmark*` or `lockup*`; resolved as expected for lettering. Latest review: `review.md`, verdict in that file.

## Legal notes (brd:LGL-01)

Warnings only, not legal advice. These notes cover the United States only; other jurisdictions were not researched. Sources and recheck dates: `brand-core/references/legal.md` in the brand-studio plugin.

- **Copyright.** This identity was drafted with an AI model. In the US, the Copyright Office's view is that prompts alone do not make a person the author of the output; human selection, arrangement and changes may be protectable. The mark as drawn may not be protected by copyright. (US Copyright Office report on copyrightability, January 2025, and the Supreme Court's refusal to hear Thaler v. Perlmutter, March 2026; checked 2026-11-18, recheck 2027-03-01.)
- **Trademark.** Nobody has checked whether this mark or name is clear to use or register. That is your job before you rely on it: search the USPTO trademark records, including its image search (a beta), and get a professional clearance search before filing. (USPTO image search beta, April 2026; checked 2026-11-18, recheck 2027-04-01.)
- **Fonts.** Space Grotesk, OFL-1.1. OFL fonts may be used in logos; check the family's own licence file. (OFL FAQ 1.1-update8; checked 2026-11-18, recheck 2027-05-01.)
- **Generators.** No hosted image or vector generator was used.
- **Resemblance.** The reviewer noted that the mark resembles generic code-bracket icons, and the designer noted it can read as an eye (brd:LGL-02). Run the searches above.

## Provenance (brd:LGL-04)

- Narrative and brief: the narrative was written by the maintainer with Claude; the brief was drafted by Claude, with the audience and positioning confirmed by the maintainer.
- Chosen concept: C (code brackets) of three, picked by the maintainer on the live page on 2026-11-27, after an independent blind review.
- Human decisions after the pick: the maintainer rejected the first brand colour (it read brown) and chose vermilion from six measured options, approved a rewritten story after an editorial review, and replaced the suggested word to own, "proven", with "checked".
- Human changes after the pick: none to the geometry. Colours, the wordmark, lockups, icons and extras were made by Claude as edits of the picked master; the maintainer reviews them before the kit is published.
