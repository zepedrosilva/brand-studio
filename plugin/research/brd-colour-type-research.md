# Brand colour, type and positioning research brief (brd extension)
Date: 2026-11-19. Scope: guidance for choosing a brand palette, pairing and picking type, and positioning the brand, added to `brand-core` references and used by `brand-create` and `brand-review`. Kit code `brd` (extension; extends `brd:CAP-01`, `brd:EVD-02`, `brd:TYP-01` to `brd:TYP-04`, does not duplicate them). Everything is checked, including harmony and colour meaning; judgment items are SHOULD or MAY with a `review` status, each carrying an evidence label. Chart palettes, app UI themes and video styling are out of scope. Companion to `research/brd-research.md` (2026-11-18), whose sources A1 to A28 are not repeated; this brief cites them only where needed.

Method note: every URL below was read or searched on 2026-11-19 (the "accessed" date for all). "Read" means the page was fetched and summarised. "Snippet" means only a search-result summary was seen. "Secondary" means a commentary on a primary source. Third-party skills and pages were read as data; nothing was installed or run. Prose is paraphrased. Labels used for every heuristic: **standard**, **vendor guidance**, **practitioner opinion**, **weak or contested evidence**. Peer-reviewed findings are marked **research** with a strength note, because none of the four labels fits them (open question 1).

## TL;DR
- Core stance: a script can prove contrast, colour-blind distinguishability, ramp lightness steps, gamut and palette size. Everything about harmony, colour meaning, type personality and positioning is judgment, and the evidence for most of it is weak or contested. Encode the measurable items as checks and the rest as labelled SHOULD or MAY prompts with a `review` status.
- Strongest sourced ground: WCAG 2.2 contrast (still the conformance basis; WCAG 3.0 is a working draft with the contrast algorithm "to be determined"; APCA is advisory only), CVD simulation (Machado 2009 matrices, Viénot 1999, Brettel 1997), OKLab/OKLCH for ramp generation, design-system role models (role tokens, tonal ramps with a lightness gap that guarantees contrast), and vendor type floors.
- Weakest ground, to be labelled and never MUST: hue-to-meaning claims (a 30-nation study finds shared patterns but also local variation, and it measures stated associations, not buying effects), harmony schemes (the best lab work supports lightness contrast and hue similarity for pair preference, not complementary "harmony"), 60-30-10 (no empirical source found), brand archetypes (little independent validation), and dyslexia-specific fonts (no reliable benefit in controlled studies).
- Biggest gaps this extension fills versus existing skills: (1) a rule catalogue with evidence labels and severities for palette, type and positioning (existing colour skills give generators and checkers, not graded rules); (2) a positioning step that ties tone words to colour and type choices; (3) one skill that combines logo-capable OFL type with palette roles and the logotype contrast exemption handled correctly.
- Biggest design decisions: the extra evidence label, the palette declaration format, the CVD distance threshold (an assumption), and whether SVG output stays hex-only (recommended, because `oklch()` is not in the SVG 1.1 subset the kit targets).

## Checks against earlier material
Items 1 and 2 confirm existing text; items 3 to 5 are corrections or cautions.
1. `thresholds.md` labels `contrast_large_or_nontext: 3.0` as standard. Confirmed: SC 1.4.3 (large text) and SC 1.4.11 (non-text) both use 3:1 (C1, C4).
2. `rules.md` EVD-02 says a brand logo "may be exempt" from contrast. Confirmed with a condition: the logotype exemption in SC 1.4.3 and 1.4.6 covers text that is part of a logo or brand name (C2). For SC 1.4.11 the Understanding page says logos are generally exempt, but not when the logo works as a control, and not when the low contrast was the author's choice rather than brand-mandated (C4). The existing wording matches; keep "report, never fail".
3. Material's "tone gap of 50 gives 4.5:1" is a property of HCT tone (CIELAB L*), not of OKLCH lightness. Do not carry the rule over to OKLCH ramps; compute contrast directly (derived, see topic 6).
4. A widely repeated claim that "62 to 90 percent of snap judgments rest on colour alone" traces back to a secondary paper and is not backed by primary data (C25). Never encode it.
5. Secondary pages mention a pooled analysis of 15 dyslexia-font studies (688 readers) with no reliable effect; it was not verified against the paper (C32). Treat as unverified.

## Deterministic versus judgment (what a script can decide)
| Item | Script (S) or judgment (J) | Basis | Note |
|---|---|---|---|
| WCAG contrast ratio of each declared role pair | S | C1, C2 | Formula and sRGB constants are fixed; do not round (4.499 fails 4.5). |
| Large-text classification from size and weight | S | C1 | At least 18 pt, or at least 14 pt bold; 24 px and 18.5 px bold are the common conversions (C2). |
| Non-text pair at least 3:1 | S | C4 | Applies to UI parts and meaningful graphic parts; logos report only. |
| CVD-simulated distance for role pairs that must be told apart | S | C13, C14, C15 | Simulate deutan, protan and tritan at severity 1.0 in linear RGB, then measure distance in Oklab. The pass threshold is an assumption (topic 2). |
| Lightness difference as a non-colour cue | S | C3 | SC 1.4.1 accepts a 3:1 lightness-based contrast as an additional cue. |
| OKLCH ramp: monotonic lightness, in-gamut, step sizes | S | C9, C10 | Generation aid; verify contrast separately. |
| Palette size: count of distinct hues (within a hue window) and declared roles | S | practitioner (T2) | Hue window of 15 degrees is practitioner opinion. |
| Role coverage: primary, neutral, background and text roles declared | S | vendor pattern (C38, C39, C41) | Presence check only. |
| Dark and light variants both declared and both verified | S | C34, C38 | |
| Colours on the brief's avoid list (hue within a window) | S | the brief | Window is an assumption. |
| Font licence record, family count, available weights, glyph coverage of the brand name | S (needs the font file; fontTools optional) | existing TYP rules, C35 | Detect only when a file is given. |
| Minimum size and weight floors for stated text uses | S | C35 | Vendor floors, not standards. |
| Harmony fit, colour-meaning fit, tone-to-type fit, category differentiation, distinctiveness, positioning quality, archetype choice | J | C18 to C24, C27 to C29 | `review` status, SHOULD or MAY only. |

## Sources (track A)
Source ids use the prefix C (colour and type) to avoid clashing with A1 to A28 in the earlier brief. Accessed 2026-11-19 for every row.

| # | Source | Type and label | Page date | Key points |
|---|---|---|---|---|
| C1 | WCAG 2.2 https://www.w3.org/TR/WCAG22/ | Standard (W3C Recommendation) | 2024-12-12 version of the 2023-10-05 Recommendation (read, first 100k of 270k characters) | Contrast ratio formula; large-scale text is at least 18 pt or 14 pt bold. |
| C2 | Understanding SC 1.4.6 https://www.w3.org/WAI/WCAG22/Understanding/contrast-enhanced.html | Standard | no date shown | AAA 7:1 for text, 4.5:1 for large text; logotypes and brand names exempt; brand guidelines do not exempt other text; ratio is (L1+0.05)/(L2+0.05) with sRGB constants (0.04045 split, 2.4 exponent); computed values must not be rounded. |
| C3 | Understanding SC 1.4.1 https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | Standard | 2025-09-16 | Colour must not be the only visual means; a lightness difference with at least 3:1 counts as an additional cue; red/green meaning still needs a non-colour indicator. |
| C4 | Understanding SC 1.4.11 https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | Standard | 2026-10-04 | 3:1 for UI component boundaries and meaningful graphic parts; logos generally exempt unless a control or low contrast by author choice; focus and selection states covered; hover-only change not required to contrast. |
| C5 | Understanding SC 1.4.12 https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | Standard | no date shown | Content must survive user-applied spacing of 1.5 line height, 2x paragraph spacing, 0.12 letter spacing, 0.16 word spacing (multiples of font size). These are tolerance values, not authoring minimums. |
| C6 | WCAG 3.0 https://www.w3.org/TR/wcag-3.0/ | Standard in progress (Working Draft) | 2026-09-10 | Contrast algorithm "yet to be determined"; placeholders in the text-contrast requirement; editors assume a size and weight factor and may need a separate red/green requirement; not to be cited as final. APCA not named in the text read. |
| C7 | W3C WAI news, WCAG 2.2 as ISO/IEC 40500:2025 https://www.w3.org/WAI/news/2025-10-21/wcag22-iso | Standard status (snippet) | 2025-10-21 | The ISO text equals the 2023-10-05 Recommendation; the 2024-12-12 version is expected as a 2026 ISO edition. Page not opened. |
| C8 | APCA https://github.com/Myndex/SAPC-APCA and https://github.com/Myndex/apca-w3 | Practitioner/spec group, beta (read) | formula 0.0.98G-4g; constants unchanged since 2021-02-15; library 0.1.9 released 2022-07-03 | Method for emerging WCAG 3, not part of WCAG 2.x; non-text guidance is a placeholder; licence is a limited collaborative one (read LICENSE.md before copying code). Lc 75 for fluent body text and Lc 90 preferred appear in secondary summaries seen in a search, not in the page text read. |
| C9 | Ottosson, "A perceptual color space for image processing" https://bottosson.github.io/posts/oklab/ | Primary technical post | 2020-12-23; matrices updated 2021-01-25 | Oklab predicts lightness, chroma and hue as separable axes; fixes CIELAB hue problems in blue and the HSV lightness mismatch; author states his lightness and chroma data came from CAM16, not new human experiments, and assumes normal viewing; gives matrices and test pairs. |
| C10 | CSS Color 4 https://www.w3.org/TR/css-color-4/ | Standard in progress (Candidate Recommendation Draft) | 2026-11-18 | `oklab()` and `oklch()` defined; gamut-mapping algorithms for RGB destinations; HSL green is 120 degrees but about 134 degrees in LCH, so hue angles differ by space. The JND of 0.02 for deltaEOK in the gamut-mapping pseudocode comes from a 2021 draft seen in search results (secondary to this page, not re-read in the 2026 text). |
| C11 | CSS Color 5 https://www.w3.org/TR/css-color-5/ | Standard in progress (Working Draft) | 2026-11-16 | `color-mix()` defaults to Oklab; relative colour syntax; `light-dark()` and `contrast-color()` added; draft says not for citation as final. |
| C12 | MDN `contrast-color()` https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/contrast-color | Vendor docs | Baseline 2026, newly available since April 2026 | Returns white or black, whichever contrasts more; browsers may use other algorithms; mid-tone backgrounds can fail small text with both. |
| C13 | Machado, Oliveira, Fernandes 2009, IEEE TVCG 15(6) https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html | Peer-reviewed research, widely implemented (read matrices page) | 2009 | Severity 0.0 to 1.0 in 0.1 steps; 1.0 is dichromacy; interpolate between matrices; three 3x3 matrices at 1.0 (rows sum to 1, so white is preserved; checked by hand on the values read). The page labels the sets "-anomaly" although 1.0 is dichromacy. The page does not state linear versus gamma input; an R package paper (C16) applies them to linear RGB by default. |
| C14 | Viénot, Brettel, Mollon 1999, Color Res. Appl. 24(4) https://onlinelibrary.wiley.com/doi/10.1002/(SICI)1520-6378(199908)24:4%3C243::AID-COL5%3E3.0.CO;2-3 ; Brettel, Viénot, Mollon 1997, JOSA A 14(10) | Peer-reviewed research (snippet plus C15) | 1999 / 1997 | Single-matrix simulation of protanopia and deuteranopia for sRGB monitors, simplified from Brettel 1997. |
| C15 | DaltonLens, "Understanding LMS-based colour blindness simulations" https://daltonlens.org/understanding-cvd-simulation/ | Practitioner write-up (read) | no date shown | All these methods run in linear RGB: decode sRGB, convert to LMS, simulate, convert back, re-encode; skipping decoding makes colours too dark; author recommends the Smith and Pokorny LMS transform with D65 white; full dichromacy assumed; tritan section not in the text read. |
| C16 | Zeileis et al., colorspace toolbox https://arxiv.org/pdf/1903.06490 | Peer-reviewed software paper (snippet) | 2019 | Uses the Machado model; matrices applied to linearised RGB by default; evaluates palettes under deutan, protan, tritan and desaturation. |
| C17 | MedlinePlus Genetics, colour vision deficiency https://medlineplus.gov/genetics/condition/color-vision-deficiency/ | Public health reference (read) | 2026-10-21 | About 2.5 percent of people worldwide; red-green about 1 in 12 men and 1 in 200 women in Northern European populations; blue-yellow under 1 in 10,000 with equal rates by sex. |
| C18 | Schloss and Palmer 2011, Attention, Perception and Psychophysics 73(2) https://palmerlab.berkeley.edu/pdf/Schloss&Palmer(2011).pdf | Research, moderate strength (search summary; paper not opened) | 2011 | For colour pairs: preference and harmony rise with hue similarity; preference depends more on lightness contrast and on liking of the component colours; no support for hue-contrast "harmony"; harmony higher for lighter and similarly saturated pairs. Pairs, not whole palettes; lab ratings. |
| C19 | Palmer and Schloss 2010, PNAS 107(19) https://pubmed.ncbi.nlm.nih.gov/20421475/ | Research, moderate to strong (summary) | 2010 | Colour preference tracks the average liking of objects associated with the colour (a later paper reports about 80 percent of variance). This is about liking, not meaning or sales. |
| C20 | Valdez and Mehrabian 1994, J. Exp. Psych.: General 123(4) https://www.ovid.com/journals/jepge/abstract/10.1037/0096-3445.123.4.394~effects-of-color-on-emotions | Research, moderate (abstract level) | 1994 | Brightness and saturation had strong, consistent effects on pleasure, arousal and dominance; hue effects were smaller. Munsell chips in a lab. |
| C21 | Jonauskaite et al. 2020, Psychological Science 31(10) https://doi.org/10.1177/0956797620948810 | Research, moderate (search summary) | 2020 | 4,598 people in 30 nations, 12 colour terms against 20 emotion concepts; overall similarity r = .88, plus local differences that track linguistic and geographic closeness; red links to both love and anger. Stated associations to colour words, not effects. |
| C22 | Labrecque and Milne 2012, J. Acad. Marketing Sci. 40 https://link.springer.com/article/10.1007/s11747-010-0245-y | Research, moderate (summary) | 2012 | Hues map to brand-personality dimensions in experiments (red to excitement, blue to competence); shade (saturation, lightness) shifts the signal. |
| C23 | Elliot and Maier 2014, Annual Review of Psychology 65 https://www.annualreviews.org/content/journals/10.1146/annurev-psych-010213-115035 | Research review (abstract) | 2014 | Colour can carry meaning and affect affect, cognition and behaviour; earlier work was hampered by method problems; the review focuses on achievement, attraction, consumer and food contexts. Full text not read (403). |
| C24 | Bottomley and Doyle 2006, Marketing Theory 6(1) https://www.semanticscholar.org/paper/The-interactive-effects-of-colors-and-products-on-Bottomley-Doyle/553ace4aba7f25c15d990cf74ba82599f907c475 | Research, moderate (summary) | 2006 | Logo colour is judged more appropriate when it fits the product type (functional colours for functional products, sensory-social colours for sensory-social ones); later work calls this category colour norms. |
| C25 | Singh 2006, Management Decision, and its repeated "62 to 90 percent" claim https://www.researchgate.net/publication/235320162_Impact_of_color_on_marketing | Secondary paper plus attribution trail (snippet) | 2006 | Often cited as the origin of the claim; attributions drift and none reach primary data. Another skill's evidence file calls it a misquoted review (T1). Weak or contested. |
| C26 | Henderson and Cote 1998, J. Marketing 62(2) https://journals.sagepub.com/doi/abs/10.1177/002224299806200202 | Research, moderate (summary) | 1998 | Over 195 logos: high-recognition logos should be natural, harmonious and moderately elaborate; elaborateness has an inverted-U relation with pleasingness. |
| C27 | Henderson, Giese, Cote 2004, J. Marketing 68(4) https://www.researchgate.net/publication/242049625_Impression_Management_Using_Typeface_Design | Research, moderate (summary) | 2004 | Six typeface dimensions (elaborate, harmony, natural, flourish, weight, compressed) predict impressions such as pleasing, engaging, reassuring and prominent; weight trades prominence against the others. |
| C28 | Brumberger 2003, Technical Communication 50(2) https://www.ingentaconnect.com/content/stc/tc/2003/00000050/00000002/art00007 | Research, moderate (snippet) | 2003 | Readers consistently ascribe personality to typefaces; a typeface-text mismatch did not change how readers judged the text. Practitioner type-personality lore had little empirical backing before this. |
| C29 | Xu, Chen, Liu 2017, Marketing Letters https://link.springer.com/article/10.1007/s11002-016-9415-0 ; later studies found in the same search | Research, moderate to weak (summary) | 2017 | Lowercase wordmarks read as friendlier, uppercase as stronger and more authoritative; wordmark complexity weakens the effect; a later study ties uppercase preference to luxury level. A 2024 Memory and Cognition study found changing font or case slowed brand-name recognition. No empirical study on tracking in wordmarks was found. |
| C30 | Kuster et al. 2018, Annals of Dyslexia 68 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5934461/ | Research, moderate to strong (summary) | 2018 | 170 children with dyslexia read no faster or more accurately in a dyslexia font than in a common sans; they preferred common fonts. |
| C31 | Wery and Diliberto 2017, Annals of Dyslexia 67(2) https://eric.ed.gov/?id=EJ1156546 | Research, small sample (summary) | 2017 | No gain in reading rate or accuracy from OpenDyslexic against two common fonts; no participant preferred it. |
| C32 | Marinus et al. 2016, Dyslexia 22(3) https://www.semanticscholar.org/paper/A-Special-Font-for-People-with-Dyslexia:-Does-it-Work-and-if-so-why-Marinus-Mostard/8948db1648758f6c752db374988c292e04e094d2 ; Rello and Baeza-Yates 2013 https://www.changedyslexia.org/publications/pdfs/2013-ASSETS-Good%20Fonts%20for%20Dyslexia.pdf ; a pooled-study claim (15 studies, no reliable effect) seen only in secondary pages | Research, mixed (summaries) | 2016 / 2013 | The small 7 percent gain in one study was attributed to the font's spacing, not its letter shapes. In the 2013 eye-tracking study (48 readers) sans-serif, monospaced and roman styles helped some measures and italics hurt, mostly through fixation duration, and OpenDyslexic did not help. The pooled-study claim is unverified. |
| C33 | BDA Dyslexia Style Guide (2018 mirror) https://iped-editors.org/wp-content/uploads/2021/05/British-Dyslexia-Association-Style-Guide-2018.pdf ; International Dyslexia Association page https://dyslexiaida.org/do-special-fonts-help-people-with-dyslexia/ (403, not read) | Institutional guidance (snippet) | 2018 / 2023 | Guide recommends sans-serif at 12 to 14 pt, 1.5 line spacing, bold instead of italics or underline, avoiding continuous capitals; one source says the BDA took the guide down in 2026. A 2026 review calls the sans-serif advice institutional rather than research-derived. |
| C34 | Apple HIG, color https://developer.apple.com/design/human-interface-guidelines/color | Vendor guidance (read via the page's JSON) | change log 2025-12-16 | Colours must work in light, dark and Increased Contrast; do not use colour alone; avoid hard-to-tell pairs; colour meaning differs by culture (a market-specific example is given); provide light and dark variants and an increased-contrast variant; test in varied lighting. No numeric ratios on this page. |
| C35 | Apple HIG, typography https://developer.apple.com/design/human-interface-guidelines/typography | Vendor guidance (read) | 2025-12-16 | Defaults and minimums by platform: iOS and iPadOS 17 and 11 pt, macOS 13 and 10 pt, tvOS 29 and 23 pt, visionOS 17 and 12 pt, watchOS 16 and 12 pt; avoid ultralight, thin and light weights; use as few typefaces as possible; thin custom fonts need larger sizes; custom fonts must support Dynamic Type and Bold Text. |
| C36 | Apple HIG, accessibility https://developer.apple.com/design/human-interface-guidelines/accessibility | Vendor guidance (read) | 2025-06-09 | Contrast guide from WCAG AA: 4.5:1 up to 17 pt, 3:1 at 18 pt and for bold at any size; APCA mentioned as an alternative without thresholds; red-green and blue-orange pairs need extra care; prefer system colours with accessible variants. |
| C37 | material-color-utilities concepts https://github.com/material-foundation/material-color-utilities/blob/main/concepts/contrast_for_accessibility.md and the repository README | Vendor guidance (read) | no date shown | HCT is hue, chroma and tone (CAM16 with L*); a tone difference of 40 guarantees at least 3:1 and 50 guarantees at least 4.5:1; hue and chroma are ignored by the guarantee. The Material 3 site pages (roles, how the system works) did not render in the fetch tool, so role counts there are not read. |
| C38 | Atlassian design, colour https://atlassian.design/foundations/color | Vendor guidance (read) | no date shown | Ten semantic roles (neutral, brand, information, success, warning, danger, discovery, accent, inverse, input); accent colours carry no meaning and are swappable; emphasis levels; AA contrast 3:1 for essential UI and text at 24 px and above, 4.5:1 below; pair selection with a non-colour cue; light and dark themes by token. |
| C39 | IBM Carbon colour https://carbondesignsystem.com/elements/color/overview/ and https://carbondesignsystem.com/elements/color/usage/ | Vendor guidance (read) | no date shown | Ten grades per hue plus black and white; the number of grade steps between two colours indicates contrast (five steps for 4.5:1 and four for 3:1 between grade 100 and 50); neutral grey dominates and one core blue is the action colour, other hues used sparingly; role tokens by layer. |
| C40 | Primer colour https://primer.style/foundations/color | Vendor guidance (read) | no date shown | Functional tokens for foreground, background, border and shadow, and pattern tokens; page content on contrast and colour-blind themes was not in the text read. |
| C41 | Radix Colors scale https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale | Vendor guidance (read) | no date shown | 12 steps with fixed jobs: 1 to 2 backgrounds, 3 to 5 component states, 6 to 8 borders and focus, 9 to 10 solid fills, 11 to 12 text; steps 11 and 12 reach Lc 60 and Lc 90 on a step 2 background. |
| C42 | Tailwind CSS colours https://tailwindcss.com/docs/colors | Vendor guidance (read) | docs for v4.3 | Default palette defined in OKLCH (black and white in hex); 26 hues with 11 shades each (50 to 950). |
| C43 | Google Fonts Knowledge, pairing https://fonts.google.com/knowledge/choosing_type/pairing_typefaces and the font-matrix page https://fonts.google.com/knowledge/choosing_type/pairing_typefaces_based_on_their_construction_using_the_font_matrix | Vendor guidance (snippet) | no date shown | Pick a secondary face different enough but not too different; pair faces from the same form model but differing in contrast and serifs; avoid pairing faces from the same matrix row; a single family or superfamily may be enough, and a second face earns its place only if it does something the first cannot. |
| C44 | google/fonts licence metadata, e.g. https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/METADATA.pb | Vendor data (read per family) | read 2026-11-19 | The `license` field is OFL for Inter, Fraunces, Space Grotesk, Manrope, Playfair Display, Bricolage Grotesque, IBM Plex Sans, DM Sans, Instrument Serif and Sora. Directory name (`ofl`, `apache`, `ufl`) is the first hint; the family's own licence file still has to be read (existing `brd:TYP-02`). |
| C45 | Bringhurst, The Elements of Typographic Style, via secondary notes https://mitchellkember.com/books/bringhurst and https://www.viget.com/articles/the-line-length-misconception | Practitioner authority, secondary (snippet) | n/a | Start with a single family; choose type that honours the character of the text; 45 to 75 characters per line is satisfactory and about 66 ideal for a single-column serif text page; a web-focused critique argues longer lines read acceptably. Book not read. A "few families" rule was not found verbatim. |
| C46 | Lupton, Thinking with Type https://www.thinkingwithtype.com/ | Practitioner authority | n/a | Fetch failed twice, so no claim is made from it. Listed as an unread primary. |
| C47 | Positioning: Ries and Trout, Positioning (1981); Moore, Crossing the Chasm (1991); Dunford, Obviously Awesome, as compared at https://www.articos.com/blog/positioning-frameworks | Practitioner books via a secondary comparison (snippet) | n/a | Ries and Trout: positioning acts on the prospect's mind, aim to own one word or position, be first or reposition the leader; Moore template: for, who, that, unlike; Dunford: ten steps from competitive alternatives to value to segment. Books not read. |
| C48 | Aaker 1997, J. Marketing Research 34(3) https://journals.sagepub.com/doi/abs/10.1177/002224379703400304 | Research, moderate (abstract and summaries) | 1997 | Five brand-personality dimensions (sincerity, excitement, competence, sophistication, ruggedness) from a 42-trait scale. The dimensions describe perceived personality; they do not prescribe colours. |
| C49 | Critiques of brand archetypes https://www.thedrum.com/opinion/yes-brand-archetypes-are-pseudoscience-does-make-them-completely-useless ; https://cdr.lib.unc.edu/downloads/st74cv57x | Practitioner opinion plus a student thesis (snippet) | n/a | The twelve brand archetypes come from a 2001 marketing book, not from Jung; independent validation is scarce; defenders treat them as a storytelling heuristic. Weak or contested as science. |
| C50 | Distinctive assets: Sharp, How Brands Grow; Romaniuk, Building Distinctive Brand Assets (2018), via secondary pages such as https://www.distinctivebat.com/distinctive-brand-assets/ and https://www.untappedprofits.co/one-brain/creative-production/brand-codes/ | Research-based practitioner books, secondary (snippet) | n/a | An asset is useful when famous and unique, built by consistency; colour alone is a weak asset because categories share palettes (secondary claim, not seen in a primary page); colour works through learned association, not meaning. The Institute's own page fetched did not define the terms. Books not read. |
| C51 | Brand guidelines contents (several practitioner guides, e.g. https://www.frontify.com/en/guide/brand-guidelines) | Practitioner opinion (snippet) | n/a | Typical sections: brand foundation (purpose, positioning, audience, personality), logo with clear space, minimum size and misuse, colour with proportions and accessible pairs, typography with hierarchy and licensing, voice, applications, governance; a one-page minimum is logo files, colour codes, font names, clear space and minimum size. |
| C52 | 60-30-10 rule (search of several interior-design and design guides) | Weak or contested | n/a | No empirical study and no traceable origin found; sources call it a guideline and proportions, not measurements. |
| C53 | axe-core colour contrast rule https://dequeuniversity.com/rules/axe/html/4.10/color-contrast | Tool docs (read) | rule version 4.10 | Mechanical WCAG 2 AA check; cannot decide text on images, gradients, pseudo-element backgrounds or some overlaps and marks those for manual review (a model for our `review` status). |

Not used: published case notes from branding agencies. The few found were promotional and not citable for method; none is relied on.

## Existing skills and tools (track B)
Signals read 2026-11-19. Star counts on directory sites disagree; only GitHub page counts are given as read, otherwise marked "directory".

| Name | Publisher | Signal | Covers | Borrow | Gaps vs our intent | License |
|---|---|---|---|---|---|---|
| T1 color-palette-designer https://github.com/visualife/color-palette-designer-skill | visualife (individual) | 1 star, 9 commits | Skill plus Node CLI: brief to light and dark palette; each colour is a named role in OKLCH, solved on lightness only until WCAG 2.2 passes; APCA advisory; Machado simulation with an Oklab distance; dark-mode rules where FAIL blocks and WARN needs a stated reason; area-split presets; scored font-pairing library with nine checks; `references/evidence-and-conventions.md` grading claims | The evidence file idea (standards versus research versus conventions versus contested, with the misquoted-statistic warning); "solve lightness only, keep hue and chroma" as the generation rule; FAIL versus WARN-with-reason gate; area splits labelled as conventions | Almost no popularity signal; no logo, wordmark or positioning; Node, not Python; no licence shown | not shown on the page |
| T2 better-colors, better-typography https://github.com/jakubkrehel/skills | jakubkrehel (individual) | 12.4k stars, 484 forks, 185 commits on the repository, 16 skills | Colour: few ramps (one neutral, one accent, only the status ramps used); each ramp step has a role; semantic tokens by role; hues within 15 degrees of OKLCH hue count as the same colour; light-end step of about 0.04 to 0.05 L; one filled primary action per view; reports failing pairs without changing colours; "Not verified" for anything not run. Type: scale, hierarchy, measure 60 to 75, body line height 1.5 to 1.6, rarely more than three families, weight 400 or more below 18 px, size floors | The role-per-step model; the 15 degree "same colour" window; the report-not-fix stance; the "Not verified" convention; type heuristics as labelled opinion | Product-UI focus; no CVD, no brand positioning, no logo; says harmony and psychology are not covered | MIT (repository) |
| T3 Brand-building-skills https://github.com/arnabbagxd/Brand-building-skills | arnabbagxd (individual) | 893 stars, 110 forks, 8 commits, 29 skills | Brand context, strategy, naming, identity, voice, guidelines, positioning (competitive landscape, territory, positioning statement, proof points); each skill under 500 lines with evals and references | The positioning artifact set (landscape, territory, statement, proof points) and a shared brand-context file | No colour or type rules; inputs and outputs of the positioning skill not shown on the page; no checks | MIT |
| T4 color-accessibility-audit https://github.com/georgekhananaev/claude-skills-vault/tree/main/.claude/skills/color-accessibility-audit | georgekhananaev (individual) | star count not shown (folder view) | Python scripts: pair checker with optional CVD simulation, scanners for CSS, JS, Tailwind and SVG fill and stroke; WCAG 1.4.1, 1.4.3, 1.4.6 and 1.4.11 thresholds; a fixer that holds hue and saturation in HSL and searches lightness | SVG colour scanning as a model for reading the palette from an SVG; the contrast and CVD pair-report shape | HSL fixer (not perceptual); CIE76 distance with thresholds 10 and 3 is crude and unsourced; licence not shown | not shown on the page |
| T5 frontend-design https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md | Anthropic (official repository) | official repository; directory listings give very large star counts that disagree | About 71 lines: ground the design in the subject, plan a compact token system with 4 to 6 named colour values, name generic defaults to avoid, one family or two clearly distinct, line length under about 80, concentrate boldness in one element | "Name the clichés, then choose deliberately" (fits our CNC-01 category clichés for palette and type); a 4 to 6 colour plan as a size cap; restraint | UI-focused; the avoid list is a moving fashion snapshot, so do not copy it as rules | per-skill LICENSE.txt (not read) |
| T6 brand-guidelines (collection) https://github.com/alirezarezvani/claude-skills (skill path returned 404 when opened) | alirezarezvani (individual) | directory listing: about 25.9k stars for the collection (2026-09 per one directory) | Visual and verbal rules, positioning, tone, colour, type, logo use, consistency audits (listing text only) | Brand-consistency audit shape | Skill page not read; star count is for the whole collection | not read |
| T7 Leonardo https://leonardocolor.io/ | Adobe open source | npm module `@adobe/leonardo-contrast-colors` | Scales generated from target contrast ratios or lightness; exports SVG, CSS variables and design tokens; colour-blind-safe palette tools | Contrast-targeted ramp generation as the model for a script (solve lightness to hit a ratio) | JavaScript; the page names neither colour spaces nor licence | not named on the page |
| T8 ColorAide https://facelessuser.github.io/coloraide/ | facelessuser (individual) | not read | Pure Python library: OKLCh, HCT, CAM16, contrast, deltaE, CVD filters | A reference implementation to test our stdlib maths against (never a runtime dependency) | Dependencies and licence not read on the page | not read |
| T9 Color.js https://colorjs.io/docs/ | maintained by the editors of CSS Color 4 and 5 | not read | JavaScript library with colour spaces, contrast, delta E, gamut mapping | Spec-aligned test vectors for OKLab and gamut mapping | JavaScript; details not read | not read |
| T10 Radix Colors and Tailwind palettes (C41, C42) | Radix, Tailwind | read | 12-step functional scale and an 11-step OKLCH palette | Step-to-job tables as vocabulary for role ramps | Product UI, not brand identity | not read |
| T11 Palette generators: Coolors, Huemint, Realtime Colors | vendors | snippet (roundups) | Coolors generates swatches from harmonies; Huemint uses machine learning and shows palettes on sample designs; Realtime Colors previews on a layout with AA/AAA per pair | The preview-in-context idea (brand sheet mockup) | Flat swatches; contrast shown but not driven; vendor-level details only | proprietary |
| T12 axe-core colour-contrast (C53) | Deque | read | Mechanical WCAG 2 check with a "needs review" outcome | The three-state result (pass, fail, incomplete) maps to `pass`, `fail`, `review` | Cannot judge gradients or images | not verified |
| T13 `contrast-color()` (C12) | browsers | Baseline 2026 | Picks black or white text for a background | Awareness only; our script computes the ratio itself | UA-defined algorithm; black or white only | n/a |
| Others, snippet only | color-master (bolasblack), color-accessibility (SkillMedev), color-palette (jezweb), design-color (tinh2), brandkit (plugin87) | not read | Palette conversion, harmony generation, contrast and CVD checks, 11-shade OKLCH ramps, DTCG tokens | Confirms that OKLCH ramps with token output and WCAG gates are now the common baseline | Not opened; no analysis | not read |

Not found: any skill that grades colour, type and positioning rules by evidence strength and ties them to a logo and wordmark review. The closest (T1) is a palette generator with an evidence file.

## Topic findings and implications for the kit

### 1. Colour theory for brand palettes
Findings:
- Colour models. HSL and HSV are device models: at the same HSV value, yellow, magenta and cyan look much lighter than red and blue (C9). Oklab and OKLCH separate lightness, chroma and hue better than CIELAB, especially in blue; the author notes the data came from CAM16 rather than new experiments (C9), and CSS Color 4 now defines both functions (C10). Tailwind v4.3 ships its default palette in OKLCH (C42). Material uses HCT (CAM16 hue and chroma with L* tone) so that a tone gap gives a contrast guarantee (C37). Hue angles differ by space (C10).
- Role-based palettes. Design systems define colour by role, not by swatch: ten semantic roles with swappable non-semantic accents (C38), twelve steps with fixed jobs (C41), ten grades whose spacing encodes contrast (C39), and a neutral-dominant system with one action colour (C39). These are vendor guidance for product UI, but the structure carries over to a brand sheet.
- Palette size. No standard gives a number. Vendor patterns: one neutral ramp, one action or brand ramp, other hues sparingly (C39); one neutral, one accent and only the status ramps the product renders (T2); a plan of 4 to 6 named values (T5). All are practitioner or vendor patterns.
- Harmony schemes. The best controlled work on pair aesthetics finds pair preference and harmony rise with hue similarity, preference depends more on lightness contrast and on liking of each colour, and there is no support for complementary "harmony of contrast" (C18). It studies pairs rated in a lab, not branded palettes. Colour preference itself is explained mostly by liking of associated objects (C19). Weak or contested for any prescriptive scheme.
- 60-30-10. No empirical source or origin found (C52). The visualife evidence file also calls proportions and harmony models conventions without usability validation (T1). Label weak or contested; use only as a starting split.
- Neutrals, tints, dark and light variants. Vendor guidance requires light, dark and increased-contrast variants of custom colours (C34) and per-theme token values (C38). A rule against pure black and pure white in dark mode comes from one individual skill (T1): practitioner opinion. Tinted neutrals are common practice but no source above states a rule.
- Generation aids. Light-end step of about 0.04 to 0.05 OKLCH L and a 15 degree "same colour" window are practitioner values (T2).

Implications for the kit:
- Candidate rules (ID-less):
  - SHOULD, vendor guidance: the palette declares roles (at least brand or action, neutral, background, text), not a loose list of hex values. Detect S (presence).
  - SHOULD, vendor guidance plus practitioner opinion: the palette has one neutral ramp and at most two brand hues, plus status colours only if the brand ships UI; distinct hues counted within a 15 degree window. Detect S. Numbers are assumptions drawn from C39, T2, T5; the existing logo master cap (`brd:CAP-01`, at most 3) is a separate budget and is kept.
  - SHOULD, vendor guidance: each declared role has both a light and a dark value, and both pass the contrast checks. Detect S.
  - SHOULD, practitioner opinion: ramps are built in OKLCH with monotonic lightness and in-gamut sRGB values, and the contrast is computed, never inferred from lightness. Detect S.
  - MAY, practitioner opinion: neutrals lean toward the brand hue at low chroma; dark mode avoids pure black background and pure white text. Detect J.
  - MAY, weak or contested evidence: the palette is not justified by naming a harmony scheme; if a scheme is claimed, the review notes the claim is a generation aid only. Detect J.
  - MAY, weak or contested evidence: area proportions (for example a dominant neutral, a secondary and a small accent) are stated as a starting split. Detect J.
- Candidate reference files in `brand-core/references/`: `palette-method.md` (role set, ramp construction in OKLCH, step-to-job table, light and dark pairing, size caps with labels) and `colour-evidence.md` (an evidence-grade table: standard, vendor, research with strength, contested), modelled on the grading idea in T1.

### 2. Accessibility
Findings:
- WCAG 2.2 is the W3C Recommendation (2023-10-05, 2024-12-12 version) and an ISO/IEC standard since 2025-10-21 (C1, C7). Thresholds: 4.5:1 for text, 3:1 for large text, 7:1 and 4.5:1 at AAA, 3:1 for non-text (C1, C2, C4). Ratios are computed without rounding (C2). Logotype text is exempt; logos are generally exempt for non-text unless they act as controls or the low contrast was a choice (C2, C4).
- APCA is a beta method for a future WCAG; the library has had no release since 2022-07-03; WCAG 3.0 (2026-09-10 draft) leaves the algorithm "to be determined" and does not name APCA in the text read (C6, C8). Vendors mention APCA without thresholds (C36). Consequence: gate on the WCAG 2 ratio; show APCA at most as advisory.
- Colour alone. SC 1.4.1 (Level A) needs a non-colour cue; a lightness difference of at least 3:1 counts as one; red/green meaning still needs an extra indicator (C3). Vendors repeat this and single out red-green and blue-orange pairs (C34, C36, C38).
- CVD testing. Machado 2009 gives three severity-1.0 matrices in a physiologically based model; Viénot 1999 and Brettel 1997 cover protanopia and deuteranopia; the methods run in linear RGB (C13 to C16). Red-green deficiency is about 1 in 12 men and 1 in 200 women in Northern European populations; blue-yellow is under 1 in 10,000 (C17). The tritan case is rare, so a tritan check is lower priority and the simulation is less well established (inference; the tritan section of C15 was not read).
- Minimum sizes. WCAG sets no minimum font size in the criteria read (inference; SC 1.4.4 resize text was not fetched). Vendor floors: 11 pt on iOS, 10 pt on macOS, 12 pt on visionOS and watchOS (C35). Text spacing tolerance values are in C5. The brief already declares `min-size` for the mark.
- Mechanical checkers cannot judge images or gradients and mark them for review (C53).

Implications for the kit:
- Candidate rules:
  - SHOULD (keep as extended `brd:EVD-02`), standard: every declared text-on-background role pair meets 4.5:1 (3:1 for large text and non-text), computed unrounded; mark and logotype report only. Detect S.
  - SHOULD, standard: pairs that carry meaning (for example success and error, or selected and unselected) also differ in lightness by at least 3:1 or carry a shape or text cue. Detect S plus J.
  - SHOULD, practitioner opinion with an assumed threshold: role pairs that must be told apart stay distinct under deutan, protan and tritan simulation (Machado 1.0, linear RGB, distance in Oklab). Assumption for the pass line: at least two just-noticeable differences of the Oklab distance (0.02 per the CSS Color 4 gamut-mapping pseudocode, C10), so 0.04; tritan reported as `review` only. Detect S.
  - MAY, vendor guidance: APCA values appear only as advisory notes, never as a verdict. Detect S.
  - MAY, standard: type specified on the brand sheet survives the WCAG text-spacing overrides (no clipped containers); applies to sheets that specify UI type only. Detect J.
  - SHOULD, vendor guidance: stated body and caption sizes respect the platform floors in `thresholds.md` (labelled vendor, not standard). Detect S.
- Candidate reference file: `accessibility-checks.md` with the formula and constants, the large-text rule, the exemptions in plain words, the three CVD matrices at severity 1.0 (to be re-read from the source page before encoding; rows sum to 1 as a sanity check), the linear-RGB rule, a worked test pair, and the policy "WCAG 2 gates, APCA advises".

### 3. Colour meaning and psychology
Findings (state plainly: contested):
- Shared patterns exist but are not universal: across 30 nations, stated colour-emotion associations correlated at about r = .88, yet nation still predicted answers beyond the shared pattern, and red links to both love and anger (C21). These are associations to colour words in questionnaires, not evidence that a brand colour changes behaviour.
- Brightness and saturation drive affect more than hue in lab ratings (C20).
- Experiments link hues to brand personality (red to excitement, blue to competence), with shade changing the result (C22).
- Congruence matters: logo colours are rated more appropriate when they fit the product type (C24). This is the research behind "category colour norms".
- Colour preference follows liking of associated objects (C19). It explains liking, not meaning.
- The review literature says colour can carry meaning and affect behaviour but notes earlier methodological weakness (C23). The widely quoted "62 to 90 percent" claim is untraceable (C25, T1).
- Vendor guidance says meaning differs by culture and shows a market-specific example (C34).
- Differentiation: colour alone is a weak distinctive asset because categories share palettes, and assets work through consistent exposure rather than meaning (C50, secondary). Primary books were not read.

Implications for the kit:
- Candidate rules:
  - SHOULD, weak or contested evidence: the palette rationale in the brief does not rely on a universal "colour means X" claim; cite the tone words and the category, not a meaning chart. The reviewer flags unsupported meaning claims as findings. Detect J.
  - SHOULD, research (moderate) plus practitioner opinion: the brief names the category's common colours and either follows them with a distinct shade or breaks them on purpose with a stated reason. Detect J, with a script check that the chosen brand hue differs from any named category hue by more than the 15 degree window or the reason is given.
  - MAY, vendor guidance: when more than one market is declared, the sheet notes known cultural variation for the chosen hues and points to local checks. Detect J.
  - MAY, research (moderate): prefer expressing tone through lightness and saturation choices, since those effects are better supported than hue effects; do not state this as a rule of thumb for any single hue. Detect J.
  - Avoid-list colours from the brief are checked against the palette. Detect S (hue window is an assumption).
- Candidate reference file: `colour-meaning.md` with a three-column table (claim, what the evidence supports, label), the shade-dependence and culture caveats, the untraceable statistics to avoid, and "what to say instead" wording for the brand sheet.

### 4. Typography for brands
Findings:
- Pairing. Vendor guidance: pair faces that differ enough and avoid combining faces from the same construction row; a single family or superfamily can suffice and a second face must do something the first cannot (C43). Bringhurst's starting point is one family (C45, secondary). Apple says as few typefaces as possible (C35). One skill says rarely more than three (T2). Another says one family or two clearly distinct (T5). No source gives a tested number; call the family count practitioner opinion with vendor support at the low end.
- Weight and size. Vendor floors and weights to avoid at small sizes (C35). A practitioner rule: weight 400 or more below 18 px (T2).
- Line length and spacing. 45 to 75 characters is satisfactory in Bringhurst's text, with web critiques (C45); WCAG tolerance values for spacing (C5); body line height 1.5 to 1.6 (T2). Relevant to the brand sheet's type specimen, not the logo.
- Typeface personality. Readers ascribe consistent personalities to typefaces (C28); six dimensions predict impressions (C27); logos work best when natural, harmonious and moderately elaborate (C26). Moderate evidence, mostly lab and older.
- Wordmark case and tracking. Lowercase reads friendlier and uppercase stronger, moderated by complexity and perceived luxury (C29); changing font or case slows recognition of a known brand name (C29). No empirical study of wordmark tracking was found; tracking advice is practitioner opinion.
- Dyslexia. No reliable benefit from dyslexia-specific fonts in controlled studies (C30, C31); a small gain in one study was attributed to spacing (C32); sans-serif and roman styles helped some eye-tracking measures and italics hurt (C32); institutional style guides recommend sans-serif at 12 to 14 pt and generous spacing, which a 2026 review calls institutional rather than research-derived (C33). Do not claim a font is "dyslexia-friendly"; support spacing, size and plain styles instead.
- Licences. Ten popular families were read as OFL in the font repository on 2026-11-19 (C44). Existing `brd:TYP-01` to `brd:TYP-04` own outlining, licence record and drawing letterforms; do not duplicate them. No Apache families were checked.
- Logo-capable families (judgment, practitioner): geometric and grotesque sans (Space Grotesk, Manrope, DM Sans, Sora, Inter, Bricolage Grotesque), humanist or corporate sans (IBM Plex Sans), and display serifs (Fraunces, Playfair Display, Instrument Serif). The shortlist is an opinion starting point; fit depends on tone and glyph coverage.

Implications for the kit:
- Candidate rules:
  - SHOULD, vendor guidance: the brand type system uses at most two families (a third only with a stated role); a second family differs in construction from the first. Detect S (count) plus J (difference).
  - SHOULD, vendor guidance: no thin or ultralight weight is used at or below the declared minimum size; the wordmark's thinnest stroke survives the minimum-size render (existing `brd:CAP-02` owns the render). Detect S where a font file is given, else J.
  - SHOULD, research (moderate) and practitioner opinion: the brief records why the typeface and case suit the tone words (one line per tone word), and notes that type personality evidence is moderate. Detect J.
  - SHOULD, research plus institutional guidance: no claim that a typeface helps dyslexia; if accessibility of type is stated, it names spacing, size and plain styles. Detect J.
  - MAY, practitioner opinion: wordmark tracking and case are recorded as deliberate decisions, with the evidence caveat. Detect J.
  - SHOULD, practitioner opinion: the font supports every glyph in the brand name, including diacritics. Detect S when the font file is available (fontTools optional, detected).
- Candidate reference files: `type-method.md` (pairing by construction contrast, family count, weight floors, line spacing for the specimen, wordmark case and tracking notes with labels, a dyslexia paragraph on what is evidenced) and `type-shortlist.md` (a dated table of OFL families with tone fit and the licence read date, re-verified at build).

### 5. Brand positioning and identity strategy
Findings:
- Positioning frameworks differ in shape: acting on the mind (own one word, be first or reposition the leader), a short fill-in template (for, who, that, unlike), or a longer evidence-first process (C47). These are practitioner books; the books were not read.
- Brand personality has one well-cited academic scale (five dimensions, C48), which describes perceived personality and does not map to colour or type.
- Archetypes (twelve types) have little independent validation and are best treated as a storytelling heuristic (C49); the earlier brief already marks archetype as optional.
- Distinctiveness: being recognised through consistent distinctive assets, rather than proven uniqueness of product, is the argument of the distinctive-asset literature (C50, secondary). Consistency is the practical rule.
- Guidelines: practitioner guides agree on contents (foundation, logo, colour, type, voice, applications, governance), and a one-page minimum is logo files, colour codes, font names, clear space and minimum size (C51). That matches the existing brand sheet.
- How colour and type express positioning is supported only weakly (topics 3 and 4), so the kit should require a stated rationale rather than a mapping table.

Implications for the kit:
- Candidate rules:
  - SHOULD, practitioner opinion: the brief carries a one-sentence positioning statement (for whom, what category, what it does, how it differs from the main alternative) and one word the brand wants to own. Detect J (presence check by S).
  - SHOULD, practitioner opinion: each of the 3 to 5 tone words (existing `brd:DEC-01`) has one line saying how palette or type expresses it. Detect J.
  - SHOULD, practitioner opinion with secondary research support: the brief names one or two ownable distinctive assets (for example a colour plus a shape) and states they stay fixed across files. Detect J.
  - SHOULD, practitioner opinion: the clichés list from `brd:CNC-01` also names palette and type clichés for the category. Detect J.
  - MAY, weak or contested evidence: an archetype or personality-dimension label may be recorded as a storytelling aid; it is never used to justify a colour.
  - MAY, practitioner opinion: the brand sheet states minimum guideline contents (colour codes with roles, font names with licence, clear space, minimum size, do and do not).
- Candidate reference file: `positioning.md` with the statement template, the "one word" test, the distinctive-asset note labelled secondary, a short note on archetype evidence, and the link from tone words to palette and type rationale lines.

### 6. Palette generation methods a script can do
Findings (all feasible in Python 3 standard library; no dependencies needed):
- WCAG contrast: sRGB decode with the 0.04045 split and 2.4 exponent, luminance weights 0.2126, 0.7152, 0.0722, ratio with 0.05 offsets, no rounding (C2). Hand check: the lightest grey that passes 4.5:1 on white is #767676 (about 4.54:1; #777777 is about 4.48:1). Derived by hand from the formula; put both in the test fixtures and verify.
- OKLab and OKLCH: two 3x3 matrices with a cube root between them; reference matrices and sample pairs are published (C9). Use a test set from the post and check against a spec-aligned library offline (T8, T9) without making either a dependency.
- Lightness-driven contrast solving: keep hue and chroma, adjust OKLCH L by bisection until the ratio passes, as the contrast-driven generators do (T1, T7). Derived relation for greys: OKLab L equals the cube root of Y, so on white 4.5:1 needs L at most about 0.568, 3:1 about 0.669 and 7:1 about 0.464 (derived by hand; assumption: achromatic only). Chromatic colours at the same L differ in Y by hue, so compute the ratio directly and never rely on L thresholds. The HCT tone-gap guarantee of 40 and 50 (C37) does not transfer to OKLCH (inference).
- Gamut: reduce chroma until the colour fits sRGB; CSS gamut mapping describes chroma reduction with a local clip and a 0.02 JND in Oklab (C10). A simple bisection on chroma is enough for a first version.
- Ramps: eleven steps (50 to 950) or twelve role steps are the common vocabulary (C41, C42); step-to-job tables are in C41. Contrast-spaced grades are a vendor pattern (C39).
- CVD: Machado severity-1.0 matrices (values read in C13; verify before encoding) applied in linear RGB, then distance in Oklab (C13 to C15). Severity interpolation is documented but only 1.0 is needed.
- Mixing and state colours: `color-mix()` defaults to Oklab (C11); our SVG output stays hex, so mixes are computed in the script and written as hex.
- SVG caveat (inference): the kit targets the SVG 1.1 subset (earlier brief, A20), where `oklch()`, `color-mix()` and `contrast-color()` are CSS features, not SVG 1.1; renderer support was not checked. Write hex in SVG, keep OKLCH in tokens and docs.

Implications for the kit:
- Candidate rules: covered in topics 1 and 2 (S rules above).
- Candidate reference-file content: a `palette-generation.md` section listing the standard sources for each formula, the test pairs, and the tolerance for float comparison; script triage for the later design (one optional script that reads the brief's palette, prints contrast, CVD distance, ramp and size findings, reuses `brdcheck.py` conventions, and writes `review` where inputs are missing). No script is proposed here beyond that.

### 7. Existing tools and skills
Covered in the track B table. Summary of what is common: OKLCH ramps, role tokens and WCAG gates are now baseline; CVD checks are rare and crude where present (CIE76 thresholds); harmony and psychology are mostly absent or folk theory; one palette generator keeps an evidence file; positioning skills exist as separate generic marketing skills; no tool combines logo, wordmark, palette and positioning with graded rules.

Implications for the kit:
- Borrow ideas: role-per-step, lightness-only solving, "report, do not fix", "Not verified" wording, FAIL versus WARN-with-reason, evidence grading file, positioning artifact set (landscape, territory, statement, proof points), SVG colour scanning.
- Do not borrow: unsourced colour-meaning lists, CIE76 thresholds, fixed palettes or font bans that track fashion.

## Heuristics
| Heuristic | Value | Label | Source |
|---|---|---|---|
| Text contrast (AA) | 4.5:1; large text 3:1; no rounding | standard (W3C) | C1, C2 |
| Large text | at least 18 pt, or at least 14 pt bold (about 24 px and 18.5 px) | standard (W3C) | C1, C2 |
| Text contrast (AAA) | 7:1; large text 4.5:1 | standard (W3C) | C2 |
| Non-text contrast | 3:1; logos generally exempt unless controls or low contrast by choice | standard (W3C) | C4 |
| Colour not the only cue | non-colour cue, or at least 3:1 lightness difference | standard (W3C) | C3 |
| Text spacing tolerance | 1.5, 2, 0.12, 0.16 times font size (user override must not break content) | standard (W3C) | C5 |
| WCAG 3 contrast algorithm | not chosen | standard in progress | C6 |
| APCA body text target | Lc 75, Lc 90 preferred; advisory | practitioner opinion (secondary summary of APCA readme) | C8 |
| Apple text minimums | 11 pt iOS and iPadOS, 10 pt macOS, 12 pt visionOS and watchOS, 23 pt tvOS | vendor guidance (Apple) | C35 |
| Apple weights to avoid | ultralight, thin, light | vendor guidance (Apple) | C35 |
| Apple contrast guide | 4.5:1 up to 17 pt, 3:1 at 18 pt and bold | vendor guidance (Apple) | C36 |
| Typeface count | as few as possible; two clearly distinct; rarely more than three | vendor guidance (Apple) at low end; practitioner opinion above | C35, T2, T5 |
| Pairing | differ in construction, avoid same matrix row, one family may suffice | vendor guidance (Google Fonts) | C43 |
| Line length | 45 to 75 characters, about 66 ideal (print-derived; contested for web) | practitioner opinion (Bringhurst, secondary) | C45 |
| Body line height | 1.5 to 1.6 | practitioner opinion | T2 |
| Tone gap for contrast | 40 gives 3:1, 50 gives 4.5:1 (HCT tone only) | vendor guidance (Material) | C37 |
| Carbon grade spacing | five steps for 4.5:1, four for 3:1 (grade 100 against 50) | vendor guidance (IBM Carbon) | C39 |
| Radix steps 11 and 12 | Lc 60 and Lc 90 on step 2 | vendor guidance (Radix) | C41 |
| Ramp vocabulary | 11 steps (50 to 950) or 12 role steps | vendor guidance (Tailwind, Radix) | C41, C42 |
| Light-end OKLCH step | about 0.04 to 0.05 L | practitioner opinion | T2 |
| Same-colour hue window | 15 degrees of OKLCH hue | practitioner opinion | T2 |
| Palette size | one neutral ramp, one action or brand ramp, other hues sparing; 4 to 6 named values in a plan | vendor guidance (Carbon) and practitioner opinion | C39, T2, T5 |
| One JND in Oklab | 0.02 (gamut-mapping parameter) | standard in progress (CSS Color 4) | C10 |
| CVD pass line (assumed) | at least 0.04 Oklab distance under each simulation | assumption (two JNDs); no source | derived from C10 |
| Colour-blind prevalence | 1 in 12 men, 1 in 200 women (red-green, Northern European); blue-yellow under 1 in 10,000 | public health reference | C17 |
| 60-30-10 | dominant, secondary, accent proportions | weak or contested evidence | C52, T1 |
| Harmony schemes | complementary, analogous, triadic as generators only | weak or contested evidence (research supports hue similarity and lightness contrast for pairs) | C18 |
| Hue to meaning | hue-emotion associations shared but culture-shaped; hue-personality links shade-dependent | weak or contested evidence (research, moderate) | C21, C22, C23 |
| Brightness and saturation drive affect more than hue | lab ratings | research, moderate | C20 |
| Category colour fit | logo colour judged more appropriate when it fits the product type | research, moderate | C24 |
| 62 to 90 percent claim | untraceable | weak or contested evidence | C25 |
| Typeface personality | six dimensions; readers attribute persona consistently | research, moderate | C27, C28 |
| Logo style | natural, harmonious, moderately elaborate for recognition | research, moderate | C26 |
| Wordmark case | lowercase friendlier, uppercase stronger, moderated | research, moderate to weak | C29 |
| Dyslexia fonts | no reliable benefit; spacing may help | research, moderate to strong against the claim | C30, C31, C32 |
| Archetypes | twelve types | weak or contested evidence | C49 |
| Distinctive assets | fame and uniqueness through consistency; colour alone is weak | practitioner opinion with research behind it (secondary) | C50 |

## Candidate principles and rule families
Principles for the extension:
1. Measure what can be measured, label what cannot: script checks for contrast, CVD distance, ramps and counts; `review` for harmony, meaning and positioning (C1 to C6, C13 to C16, C18 to C24).
2. Roles before swatches: every colour has a job and a light and dark value (C38, C39, C41).
3. Gate on the standard, advise with the rest: WCAG 2 gates; APCA and CVD heuristics advise unless the user opts in (C6, C8).
4. Do not assert colour meaning: argue from tone, category and consistency, not from a meaning chart (C21, C23, C25).
5. Differentiate on purpose: name the category's palette and type clichés, follow or break them with a reason (C24, C50, T5).
6. Few families, clear contrast between them, readable at the minimum size (C35, C43).
7. Evidence labels travel with every number (this brief).

Rule families: reuse DEC (positioning fields in the declaration), CAP (palette and type budgets), EVD (contrast and CVD evidence), TYP (type system and pairing, extending the existing wordmark rules). Propose one new family, PAL (palette roles, ramps, variants, meaning claims), and one new family, POS (positioning), if the design phase wants separate numbering; otherwise place positioning fields under DEC.

## Draft rules
IDs are placeholders for the design phase. Detect: S script, J judgment, E render. Severity respects the agreed handling: judgment items are SHOULD or MAY with status `review`; no MUST here beyond what existing rules own.

| ID | Sev | Assertion | Detect | Remediation | Source |
|---|---|---|---|---|---|
| PAL-a | SHOULD | The palette declares roles (brand or action, neutral, background, text, plus status only if the brand ships UI), each with light and dark values | S | Add the roles; derive missing values from a ramp | C38, C39, C41, C34 |
| PAL-b | SHOULD | One neutral ramp, at most two brand hues, status only if needed; hues within 15 degrees count as one | S | Merge or drop hues, or state the reason | C39, T2, T5 (assumption on the numbers) |
| PAL-c | SHOULD | Ramps are OKLCH-built with monotonic lightness and in-gamut sRGB; contrast is computed, not inferred | S | Rebuild the ramp; clip chroma | C9, C10 |
| PAL-d | MAY | Neutrals lean toward the brand hue at low chroma; dark mode avoids pure black and pure white | J | Tint or soften | T1, T2 (opinion) |
| PAL-e | MAY | No harmony scheme is used as the justification; proportions are a starting split | J | Reword the rationale | C18, C52 (weak or contested) |
| PAL-f | SHOULD | Palette rationale cites tone and category, not a universal colour meaning | J | Rewrite the rationale | C21, C23, C25 (weak or contested) |
| PAL-g | SHOULD | The category's common colours are named and followed with a distinct shade or broken with a stated reason | J (+S hue distance) | State the choice | C24, C50 |
| EVD-x | SHOULD | All declared text and UI role pairs meet 4.5:1 (3:1 for large text and non-text), unrounded; logotype and mark report only | S | Adjust lightness | C1, C2, C4 (extends existing EVD-02) |
| EVD-y | SHOULD | Pairs that must be told apart differ by at least 3:1 in lightness or carry a non-colour cue | S+J | Add a cue or change lightness | C3 |
| EVD-z | SHOULD | Role pairs stay distinct under deutan and protan simulation (and tritan as `review`); pass line 0.04 Oklab distance (assumption) | S | Change lightness, then hue | C13 to C16, C10 |
| EVD-w | MAY | APCA values shown as advisory notes only | S | none | C6, C8 |
| TYP-a | SHOULD | At most two families (a third with a stated role); the second differs in construction | S+J | Drop or replace the second face | C35, C43 |
| TYP-b | SHOULD | No thin or ultralight weight at or below the minimum size; stated body sizes meet platform floors | S/J | Use a heavier weight or larger size | C35 |
| TYP-c | SHOULD | The brief gives one line per tone word on how the typeface and case express it | J | Add the lines | C27, C28, C29 |
| TYP-d | SHOULD | No claim that a typeface helps dyslexia; type accessibility notes spacing, size and plain styles | J | Reword | C30 to C33 |
| TYP-e | SHOULD | The font covers every glyph in the brand name | S (fontTools, optional) | Pick another family or add the glyphs by hand with review | practitioner opinion |
| POS-a | SHOULD | The brief has a positioning statement and one word to own | J (+S presence) | Draft from the narrative and confirm | C47 |
| POS-b | SHOULD | Each tone word has a rationale line for palette or type | J | Add lines | C27, C48 |
| POS-c | SHOULD | One or two ownable distinctive assets are named and kept fixed across files | J | Name them | C50 |
| POS-d | MAY | Archetype or personality label recorded as a storytelling aid only | J | Reword if used to justify colour | C48, C49 |

## Technology differences
- WCAG 2 ratio versus APCA versus `contrast-color()`: the ratio is the conformance basis today; APCA is beta and not in WCAG 3's text; `contrast-color()` is UA-defined and in practice returns black or white using the WCAG 2 ratio, which can fail on mid-tones (C6, C8, C12).
- OKLCH versus HCT: HCT adds CAM16 viewing conditions and a tone that tracks L*, so a tone gap guarantees contrast; OKLCH lightness does not carry that guarantee (C9, C37; the last point is inference).
- CVD models: dichromacy-only (Brettel 1997, Viénot 1999) versus severity-aware (Machado 2009); all in linear RGB; the tritan case is rarer and less covered (C13 to C17).
- Vendor floors differ by platform and none is a standard: iOS 11 pt, macOS 10 pt, tvOS 23 pt (C35). The existing brief's 16 px minimum for the mark is a different rule.
- Contrast contexts: logotype text is exempt from 1.4.3 and 1.4.6, but UI text on brand colours is not, so keep the two checks separate (C2, C4).
- Palette formats: SVG output stays hex; tokens and docs may use OKLCH. Wide-gamut (P3) values need an sRGB fallback (T2); not researched further.
- Jurisdictions: accessibility law adoption varies; one source says the EU harmonised standard still cites an older WCAG version, with an update dated 2026-09-07 (snippet via the C7 search). Not researched beyond that.

## Aging facts
| Fact | Checked | Recheck by | Source |
|---|---|---|---|
| WCAG 3.0 is a Working Draft dated 2026-09-10; contrast algorithm "to be determined" | 2026-11-19 | 2027-03-01 | https://www.w3.org/TR/wcag-3.0/ |
| WCAG 2.2 is the W3C Recommendation (2024-12-12 version) and ISO/IEC 40500:2025; a 2026 ISO edition is expected | 2026-11-19 | 2027-01-15 | https://www.w3.org/TR/WCAG22/ ; https://www.w3.org/WAI/news/2025-10-21/wcag22-iso |
| Understanding SC 1.4.11 updated 2026-10-04; SC 1.4.1 updated 2025-09-16 | 2026-11-19 | 2027-04-01 | C3, C4 |
| APCA is beta; apca-w3 0.1.9 released 2022-07-03; algorithm constants unchanged since 2021-02-15; limited licence | 2026-11-19 | 2027-03-01 | https://github.com/Myndex/apca-w3 |
| CSS Color 4 is a Candidate Recommendation Draft (2026-11-18); CSS Color 5 is a Working Draft (2026-11-16); at-risk items include `@color-profile` and `device-cmyk()` | 2026-11-19 | 2027-03-01 | C10, C11 |
| `contrast-color()` is Baseline newly available (April 2026); algorithm is UA-defined; a switch away from WCAG 2 math is possible | 2026-11-19 | 2027-04-01 | C12 |
| Apple HIG colour and typography last change 2025-12-16; accessibility 2025-06-09; text minimums as listed | 2026-11-19 | 2027-06-30 (after the next major OS cycle) | C34, C35, C36 |
| Tailwind docs are v4.3 with 26 hues, including newer ones (taupe, mauve, mist, olive) | 2026-11-19 | 2027-03-01 | C42 |
| Material 3 role and system pages did not render in the fetch tool; tone-gap rule read from the utilities repository | 2026-11-19 | 2027-03-01 | C37 |
| MedlinePlus colour vision deficiency page updated 2026-10-21 | 2026-11-19 | 2027-10-01 | C17 |
| The 15-study dyslexia-font pooled claim is unverified; the BDA style guide may have been taken down | 2026-11-19 | 2027-03-01 | C32, C33 |
| google/fonts licence metadata read for ten families on 2026-11-19; fonts can change licence metadata or be removed | 2026-11-19 | 2027-05-01 | C44 |
| Anthropic frontend-design skill was rewritten recently (commit referenced in search); its avoid list changes | 2026-11-19 | 2027-02-01 | T5 |
| Star counts: jakubkrehel 12.4k, arnabbagxd 893, visualife 1 | 2026-11-19 | 2027-02-01 | GitHub pages |
| Machado matrix values were read from a flattened page; re-read before building tests | 2026-11-19 | before drafting | C13 |

## Design questions the research raised
Each was decided in favour of the recommendation given; the decision records in the repository's `docs/decisions/` hold the reasoning.

1. Evidence label set. The four labels do not fit peer-reviewed findings. I recommend adding a fifth, "research (strength stated)", in `thresholds.md` and `severity-and-evidence.md`, because folding research into "standard" would overstate it and folding it into "opinion" would understate it.
2. Palette declaration. I recommend keeping the one-line `palette:` field for compatibility and adding a roles block (role, light value, dark value, ramp name) to the brief template, so role, variant and CVD checks have inputs. Alternative: only extend the one-liner with a variant marker; simpler but loses roles.
3. CVD pass line. I recommend 0.04 Oklab distance (two JNDs, an assumption with no source) per simulation, with tritan as `review` only, and a lightness gap of at least 3:1 as the accepted fallback. Say if you want a stricter or looser line.
4. Palette size caps. I recommend one neutral ramp, at most two brand hues, status only for UI brands, all as SHOULD with the numbers labelled vendor pattern plus assumption, and the existing logo master cap of 3 unchanged. Confirm that two brand hues is the right ceiling for small teams.
5. SVG colour format. I recommend hex in SVG masters and OKLCH only in tokens and docs, because `oklch()` is not in the SVG 1.1 subset the kit targets (renderer support unchecked). Say if you want OKLCH in SVG anyway.
6. Colour meaning. I recommend one reference file with the evidence table and a single SHOULD finding that flags universal-meaning claims, never a rule that prescribes a hue. This checks everything while keeping contested items out of MUST.
7. Type shortlist. I recommend shipping a dated shortlist of six to eight OFL families grouped by tone, with licence read at build, and never presenting any as dyslexia-friendly. Confirm you want a shortlist at all, since fashion changes quickly.
8. Positioning format. I recommend the short fill-in statement (for, who, that, unlike) plus the "one word to own" check, because it fits one brief field. Alternative: a longer evidence-first template, heavier than the audience needs.
9. Scripts. I recommend one optional script (contrast, CVD distance, ramp and size findings) and no more, and that rule detection degrades to `review` without it. Decide in the kit design.

## Gaps in this research (honest list)
- Primary books not read: Bringhurst, Lupton (site fetch failed), Ries and Trout, Moore, Dunford, Sharp, Romaniuk, Aaker full text. Their claims here are labelled secondary or practitioner opinion.
- Research papers C18 to C24, C26 to C29 were read at abstract or summary level, not full text; effect sizes and sample details are not verified.
- Material 3 role pages and the Primer contrast pages did not yield text; Material claims rest on the utilities repository, and role-count claims for Material are not made.
- WCAG SC 1.4.4 (resize text) and the sections of CSS Color 4 and 5 beyond the first 100,000 characters were not read, so claims about `contrast-color()` rest on MDN and secondary pages.
- Tritan simulation accuracy was not verified; print colour (CMYK, spot colours) and wide-gamut handling were not researched.
- International Dyslexia Association page returned 403; the pooled dyslexia-font study and the BDA guide status are secondary only.
- Cross-cultural evidence beyond the 30-nation study and the Apple example was not researched; jurisdictions beyond the US and one EU note were not researched.
- Licences were not read for several track B tools (Leonardo, ColorAide, Color.js, Radix, axe-core); the brief borrows ideas only and copies no text.
