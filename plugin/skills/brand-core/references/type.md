# Type: families, sizes, wordmark choices and a dated shortlist

Loaded at kit step 3 (wordmark) and by reviews of a brief with a `## Rationale` section. Rules: `brd:TYP-05` to `brd:TYP-08`; outlining, licence records, kerning and model-drawn letters stay with `brd:TYP-01` to `brd:TYP-04`. Numbers: `thresholds.md`. Sources cite `research/brd-colour-type-research.md` (`C<n>`, `T<n>`), paraphrased.

## How many families (`brd:TYP-05`)

- Start with one family; a superfamily or one family in several weights is often enough. A second face earns its place only if it does something the first cannot (C43; vendor guidance; C45, Bringhurst via secondary notes; practitioner opinion).
- At most `max_type_families` (2), a third only with a stated role (C35 asks for as few typefaces as possible; vendor guidance). Another skill allows up to three (T2; practitioner opinion); the kit keeps the lower number.
- Record every family in the `type` line of `## Rationale`, joined by `+`, so the count can be checked.

## Pairing by construction

- Pair faces that differ enough, but not too much: the same underlying form model with a different contrast or serif treatment works; two faces from the same construction row do not (C43; vendor guidance).
- A second weight of the same family is not a second family and does not satisfy "differs in construction".

## Weights and sizes (`brd:TYP-06`)

- No thin or ultralight weight at or below `min_text_px` (11). One platform's guidelines advise against ultralight, thin and light weights and says thin custom fonts need larger sizes (C35; vendor guidance).
- Platform floors differ, and none is a standard (C35, vendor guidance, read 2026-11-19): iOS and iPadOS 11 pt, macOS 10 pt, visionOS and watchOS 12 pt, tvOS 23 pt. The kit uses the iOS floor and reads pt as px (assumption).
- Weight 400 or more below 18 px is practitioner opinion (T2).
- For a type specimen on the brand sheet: lines of about 45 to 75 characters (C45; practitioner opinion, secondary; contested for the web) and body line height 1.5 to 1.6 (T2; practitioner opinion). Text must survive user spacing overrides of 1.5 line height, 2 times paragraph spacing, 0.12 letter spacing and 0.16 word spacing (SC 1.4.12, C5; standard; tolerance values, not authoring minimums).

## Wordmark choices

Record case, tracking and weight as deliberate decisions in the `## Rationale` lines.

- **Case.** Lowercase wordmarks read as friendlier and uppercase as stronger, an effect weakened by a complex wordmark and tied to perceived luxury (C29; research, moderate to weak). Changing the font or case of a known name slowed its recognition (C29), so once chosen, keep it fixed (`brd:POS-03`).
- **Tracking.** No study of wordmark tracking was found; spacing advice is practitioner opinion. Inspect pairs on the display render (`brd:TYP-03`).
- **Weight.** Beside a solid mark, a heavier weight usually balances it (kit-steps, step 3); the thinnest stroke must survive the minimum-size render (`brd:CAP-02`).
- **Personality.** Readers ascribe consistent personalities to typefaces (C28), and six design dimensions predict impressions such as reassuring or prominent (C27; research, moderate, mostly older lab work). Write why the face fits each tone word; do not claim the research proves the fit.

## Glyph coverage (`brd:TYP-07`)

The font needs a glyph for every character of the name, diacritics included. With fontTools installed, `brdtext.py` reports a missing glyph; without it, check the family's character set by judgment and say so. A missing glyph means another family, or a hand-added glyph reviewed by a designer (`brd:TYP-04`).

## Shortlist (dated)

Starting points, not decisions; any OFL or Apache family is equally valid. The tone groups are the kit's own judgment (practitioner opinion). Each licence is the `license` field of the family's `METADATA.pb` in the google/fonts repository, read 2026-11-19 per C44, re-read before use. The metadata is a hint only: `brd:TYP-02` still needs the family's own `OFL.txt` read and recorded. Recheck the list by 2027-05-01 (aging fact in the brief).

| Group | Family | Suits (judgment) | Licence |
|---|---|---|---|
| Neutral, technical | Inter | Calm, exact, screen-first tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Geometric, friendly | Manrope | Modern, open, approachable tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Geometric, friendly | DM Sans | Plain, friendly, low-contrast tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Geometric, friendly | Sora | Round, confident, product-like tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Characterful grotesque | Space Grotesk | Technical with a quirk; developer tools | OFL; licence read 2026-11-19 per C44, re-read before use |
| Characterful grotesque | Bricolage Grotesque | Lively, warm, editorial tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Display serif | Fraunces | Warm, crafted, soft-serif tones | OFL; licence read 2026-11-19 per C44, re-read before use |
| Display serif | Instrument Serif | Elegant, editorial, quiet tones | OFL; licence read 2026-11-19 per C44, re-read before use |

The licence folder for each is `ofl/<family>` in the repository (for example `ofl/fraunces`); the folder name is a first hint, never the record. A serif from the last group paired with a sans from the others differs in construction (`brd:TYP-05`).

## Dyslexia and type accessibility (`brd:TYP-08`)

Never call a typeface "dyslexia-friendly".

- Controlled studies found no reliable reading benefit from dyslexia-specific fonts: 170 children read no faster or more accurately and preferred common fonts (C30; research, moderate to strong); a small study found no gain from one such font (C31; research, small sample).
- A small gain in one study was traced to the font's spacing, not its letter shapes (C32; research, mixed). In a 48-reader eye-tracking study, sans-serif, monospaced and roman styles helped some measures and italics hurt (C32).
- Institutional style guides recommend sans-serif at 12 to 14 pt, 1.5 line spacing, bold rather than italics or underline for emphasis, and no long runs of capitals (C33; institutional guidance, which a 2026 review calls institutional rather than research-derived).
- A pooled analysis of many dyslexia-font studies appears only in secondary pages and was not verified (C32); do not cite it.

What to write instead: the spacing, size and style choices themselves, for example "body 16 px, line height 1.5, bold for emphasis, no italics".
