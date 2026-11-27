# Colour: roles, ramps, contrast and evidence

Loaded at kit step 2 (palette) and by reviews of a brief with a `## Palette roles` table. Rules: `brd:PAL-01` to `brd:PAL-08`, `brd:EVD-02` to `brd:EVD-04`; numbers: `thresholds.md`. Variant files, lockups and the brand sheet are checked against the declared roles (`brd:PAL-08`), and `brdinuse.py` places the kit in applications and measures every pair there (`brd:PAL-09`): files named `reversed` or `dark` use the dark column, all others the light column, and each carries the `brand` or `text` value as its ink. The roles table takes `#RRGGBB` only; a three-digit hex is not accepted. Sources cite `research/brd-colour-type-research.md` (`C<n>`, `T<n>`), paraphrased. Chart and diagram palettes are out of scope.

The kit never prescribes a hue by its meaning. It argues from the tone words, the category and lightness contrast, and it measures what can be measured.

## Roles

Design systems define colour by job, not by swatch (C38, C39, C41; vendor guidance). The brief's table uses six roles:

| Role | Job | Required |
|---|---|---|
| `brand` | The one colour people should remember; marks, accents, actions | yes |
| `brand-2` | A second brand hue, only with a reason in the palette rationale line | no |
| `neutral` | Secondary text, borders, rules; a low-chroma ramp leaning toward the brand hue | yes |
| `background` | The surface everything sits on | yes |
| `text` | Body text | yes |
| `status` | Success, warning, error and the like; only for a brand that ships UI | no |

Size: one neutral ramp and at most `max_brand_hues` (2) brand hues, with hues within `same_hue_window_deg` (15) counted as one (`brd:PAL-02`; C39, T2, T5; practitioner opinion, the ceiling an assumption). The master's own budget stays `max_master_colours` (3, `brd:CAP-01`).

Every role has a light and a dark value (`brd:PAL-01`; C34 asks for light and dark variants; vendor guidance). Dark values avoid a pure black background and pure white text, and neutrals lean toward the brand hue at low chroma (`brd:PAL-04`; T1, T2; practitioner opinion).

## Building a ramp

Work in OKLCH, which separates lightness, chroma and hue better than HSL or CIELAB (C9; primary technical source; CSS Color 4 defines `oklch()`, C10, Candidate Recommendation Draft).

1. Convert the chosen brand hex to OKLCH (matrices in C9).
2. Hold hue and chroma. Set a lightness per step, or solve lightness by bisection until the step meets its contrast target against the background it sits on (lightness-only solving: T1, T7; practitioner and vendor tools).
3. After each lightness change, if the colour falls outside sRGB, reduce chroma by bisection until it fits; never move the hue (CSS Color 4 gamut mapping reduces chroma, C10; standard in progress).
4. Write the result as hex. Lightness falls as the step number rises (`brd:PAL-03`).
5. Compute WCAG contrast from the hex. Never infer it from OKLCH lightness: the "tone gap of 50 gives 4.5:1" rule holds for HCT tone, not for OKLCH (C37, vendor guidance; the non-transfer is an inference in the brief).

Starting guesses for greys on white, derived by hand in the brief for achromatic colours only (assumption): OKLCH lightness at most about 0.568 for 4.5:1 and about 0.669 for 3:1. Chromatic colours at the same lightness differ, so always compute.

Step names run from 50 to 950 (11 steps, C42; vendor guidance); a brand needs only the steps its roles use. Light-end steps about 0.04 to 0.05 lightness apart are practitioner opinion (T2).

SVG masters carry hex only: `oklch()` is CSS, not part of the SVG 1.1 subset the kit targets (renderer support unchecked; inference in the brief, topic 6). OKLCH may appear in the brief notes and on the brand sheet.

## Contrast pairs (`brd:EVD-02`)

Each pair is checked twice: light values on the light background, dark values on the dark background. Ratios use the WCAG 2 formula with the sRGB constants and are never rounded (C2; standard): 4.499 fails 4.5.

| Pair | Floor | Why |
|---|---|---|
| `text` on `background` | `contrast_text` (4.5) | Body text, SC 1.4.3 (C1, C2; standard) |
| `neutral` on `background` | `contrast_text` (4.5) | The neutral step in the table sets secondary text; the kit's own choice (assumption) |
| `brand`, `brand-2` on `background` | `contrast_large_or_nontext` (3.0) | Large text, UI parts and meaningful graphics, SC 1.4.3 and 1.4.11 (C1, C4; standard) |
| `status` on `background` | `contrast_large_or_nontext` (3.0) | UI parts, SC 1.4.11 (C4; standard) |
| `mark` entries of the one-line `palette` | report only | Logos are exempt only when brand-mandated and not a control (C2, C4; standard) |

A brand colour that sets body-size text (links) is a text role: pick a step that meets `contrast_text`. WCAG 3 has not chosen a contrast algorithm (C6, Working Draft 2026-09-10; recheck 2027-03-01), so the kit gates on WCAG 2 and shows no APCA verdict.

## Pairs to tell apart (`brd:EVD-03`, `brd:EVD-04`)

The pairs are `brand` against `brand-2`, and every two `status` colours, in light and in dark.

- Colour must not be the only cue; a lightness difference of at least 3:1 counts as a second cue (SC 1.4.1, C3; standard). Below `contrast_large_or_nontext`, the pair needs a named shape, text or pattern cue (`brd:EVD-03`).
- Colour-blind check (`brd:EVD-04`): decode each hex to linear RGB (C2 constants), apply the Machado 2009 severity 1.0 matrix for deutan, protan and tritan (C13; research, widely implemented), in linear RGB (C15, C16), convert the result to Oklab (C9) and take the Euclidean distance between the two colours.
- Pass line: at least `cvd_min_oklab_distance` (0.04; assumption, no source: two steps of the 0.02 value in C10) for deutan and protan. Tritan is `review` only: it is rare (under 1 in 10,000, C17; public health reference) and its simulation is less settled (inference in the brief).
- Red-green deficiency affects about 1 in 12 men and 1 in 200 women in Northern European populations (C17; public health reference), which is why deutan and protan carry the pass line.
- To fix, change lightness first (it also satisfies SC 1.4.1), then hue.
- The matrices are not copied here. The script encodes them after re-reading C13 and tests them against a reference value.

## Category colours (`brd:PAL-07`)

1. List the 2 to 4 colours the category uses most (the number is a kit choice, assumption), from the narrative, the user or a look at the main alternatives; mark them `assumed` when not checked.
2. For each, decide `follow` (a distinct shade: a different lightness or chroma, not the leader's exact value) or `break` (with a reason), and write it to `category-colours`.
3. A `break` colour should sit more than `same_hue_window_deg` (15) from every brand hue; the script checks it.

Why: logo colour is judged more appropriate when it fits the product type (C24; research, moderate). Colour alone is a weak distinctive asset because categories share palettes, so pair it with a shape (C50; practitioner opinion, secondary).

## What the evidence supports

| Claim | What the research supports | Label | Source |
|---|---|---|---|
| Complementary, triadic or analogous schemes make a palette harmonious | Pair ratings rise with hue similarity and lightness contrast; no support for complementary "harmony"; lab pairs, not brand palettes | weak or contested evidence (from research, moderate) | C18 |
| 60-30-10 proportions | No study or traceable origin; a starting split at most | weak or contested evidence | C52, T1 |
| A hue means the same to everyone ("blue means trust") | Colour-emotion links are partly shared across 30 nations (r about .88) yet vary locally; red links to both love and anger; stated associations, not effects on choice | weak or contested evidence (from research, moderate) | C21 |
| Hue drives emotion | Brightness and saturation had stronger effects than hue in lab ratings | research (moderate) | C20 |
| Hues signal brand personality | Some hue-personality links in experiments; the shade changes the result | research (moderate) | C22 |
| Colour can change behaviour | A review says it can in some contexts, after earlier method problems | research (review, abstract read) | C23 |
| Colour preference | Tracks liking of objects linked to the colour; about liking, not meaning | research (moderate to strong) | C19 |
| Logo colour should fit the category | Judged more appropriate when it fits the product type | research (moderate) | C24 |
| "62 to 90 percent of snap judgments rest on colour" | Untraceable to primary data; never cite it | weak or contested evidence | C25 |
| Meaning varies by culture | Vendor guidance warns of it, with a market example | vendor guidance | C34 |

What the kit does with this: a harmony scheme may generate options but is never the reason (`brd:PAL-05`); the palette line argues from tone through lightness and saturation, from the category, and from consistency (`brd:PAL-06`, `brd:POS-03`).

## Writing the palette line

- Instead of "blue means trust", write the lever: "calm: one low-chroma teal on tinted greys, nothing saturated on large areas".
- Name the category choice: "follows the category's blue in a darker, teal-leaning shade".
- For a second brand hue, say what it does that the first cannot.
