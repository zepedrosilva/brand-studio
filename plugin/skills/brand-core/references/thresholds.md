# Thresholds

The YAML block below is the single source for the scripts (`scripts/SPEC.md`) and for reviewers. Change a value here, never in a script. Labels: **standard** (a published standard, read during research), **verify before release** (attributed to a standard whose text was not fetched during research), **vendor guidance** (a platform or design-system vendor's published guidance, not a standard), **practitioner opinion** (repeated by practitioners, not authoritative; tune to your case), **research (strength stated)** (a peer-reviewed finding, with its strength named beside it), **assumption** (the kit's own number, no source). Full meanings: `severity-and-evidence.md`, "Source labels". Sources cite `research/brd-research.md` (`A<n>`) and `research/brd-colour-type-research.md` (`C<n>`, `T<n>`).

```yaml
max_master_colours: 3            # brd:CAP-01; practitioner opinion (kaankiziltug)
min_feature_divisor: 48          # brd:CAP-02: smallest feature is 1/48 of the mark; practitioner opinion (kaankiziltug)
test_sizes_px: [16, 32, 64]      # brd:CRF-02, brd:CAP-02; practitioner opinion (A9, A10); other skills use other sets
max_decimals: 2                  # brd:CAP-03; practitioner opinion (kaankiziltug, jezweb)
exact_angles_deg: [30, 45, 60]   # brd:CRF-03; practitioner opinion (kaankiziltug); 0 and 90 are always exact
contrast_text: 4.5               # brd:EVD-02; standard (WCAG 2.2 SC 1.4.3, A11)
contrast_large_or_nontext: 3.0   # brd:EVD-02; large text: standard (WCAG 2.2 SC 1.4.3, A11); non-text: standard (WCAG 2.2 SC 1.4.11, 3:1, fetched 2026-11-18)
concepts_at_checkpoint: 3        # /brand-create step 5; practitioner opinion (A9)
shortlist_size: [8, 12]          # brd:CNC-01; from the rule (A9)
tone_words: [3, 5]               # brd:DEC-01; from the rule
near_angle_window_deg: 3         # brd:CRF-03: a segment this close to an exact angle, but not on it, is flagged; assumption
angle_tolerance_deg: 0.05        # brd:CRF-03: a segment this close to an exact angle counts as exact (endpoints rounded to max_decimals sit about 0.01 degrees off); assumption
centre_tolerance_pct: 2          # brd:CRF-04: a mark whose centre is off by more than this share of the viewBox is flagged; assumption
anchor_review: 40                # brd:CAP-03: a path with more anchors is flagged for review; assumption, no authority behind it
max_brand_hues: 2                # brd:PAL-02; practitioner opinion (C39, T2, T5); the exact ceiling is an assumption
same_hue_window_deg: 15          # brd:PAL-02, brd:PAL-07: OKLCH hues this close count as one colour; practitioner opinion (T2)
cvd_min_oklab_distance: 0.04     # brd:EVD-04: Oklab distance after deutan and protan simulation; assumption, no source (two steps of the 0.02 gamut-mapping value in C10)
max_type_families: 2             # brd:TYP-05; vendor guidance (C35, C43)
min_text_px: 11                  # brd:TYP-06; vendor guidance (iOS floor of 11 pt, C35; read as px, assumption); platform floors differ
export_sizes_px: [16, 32, 48, 64, 128, 256, 512, 1024]  # brd:CTR-06: PNG sizes in the downloadable set (favicon, UI, app and web uses); practitioner opinion, an assumption
max_story_paragraphs: 4          # brd:POS-05: paragraphs in ## Story; practitioner opinion, an assumption (short enough to read before the mocks)
achromatic_chroma: 0.02          # brd:PAL-07: OKLCH chroma below this counts as a neutral, not a hue; assumption, no source
export_background_coverage: 0.9  # brd:CTR-06: a PNG with this share of opaque pixels has a background, so it fails unless named as a tile; assumption, no source
```

## Not thresholds

- The grid unit for `brd:CRF-03` comes from the brief (`grid-unit`), not from here.
- Palette values come from the brief's `## Palette roles` table; which role pairs are checked, and against which of the two contrast values, is in `colour.md`.
- Icon-set values (grid, stroke, padding) come from `icons/style-spec.json`; the template's defaults are practitioner opinion (jezweb: 24 grid, 2 px padding, 1.5 or 2 px stroke, round caps and joins).
- Padding balance (`brd:CRF-04`) has no numeric limit of its own; the script reports the padding numbers as `review` when the centre offset passes `centre_tolerance_pct`. The `brd:CAP-03` anchor review and the `brd:CRF-03` near-angle window are labelled assumptions in the YAML block.
