# Legal notes

Warnings only, not legal advice. **US-centred: the research covered US sources only; EU, UK and other jurisdictions were not researched.** The kit surfaces these points with sources and leaves every decision to the user. Facts that age carry a check date and a recheck date; after the recheck date, say the fact may be out of date. Source IDs refer to `research/brd-research.md`.

## Copyright of AI-assisted output (brd:LGL-01, brd:LGL-04)

- The US Copyright Office's report on copyrightability (Part 2 of its AI series, January 2025) takes the view that prompts alone do not give a user enough control to be the author of the output; protection may attach to human-authored input, to creative selection and arrangement, and to creative human changes. Source: A14; the Office's own NewsNet page was read, the report PDF was not, so quote only the NewsNet wording. Registration: the Office's 2023 guidance (88 Fed. Reg. 16190) asks applicants to disclose AI-generated material that is more than de minimis; it said it would supplement that guidance. Checked 2026-11-18; recheck 2027-03-01. https://www.copyright.gov/newsnet/2025/1060.html
- The Supreme Court declined to hear Thaler v. Perlmutter on 2026-03-02, so the human-authorship requirement stands in the US; a denial is not a ruling on the merits, and the line between AI-assisted and AI-generated work is still open. Source: A15 (law-firm summary, snippet level). Checked 2026-11-18; recheck 2027-03-01.
- What this means for the kit: the mark may not be protectable by copyright as drawn. The provenance note (`brd:LGL-04`) records what the human chose and changed, so the user can describe their contribution later. Trademark protection is a separate question.

## Trademark clearance (brd:LGL-01, brd:LGL-02)

- Clearance is the user's job. The kit never says a mark is clear or safe to register.
- One practitioner log reports sending back 4 of 10 logos in a batch review for resembling earlier ones (A9); shapes such as a spinner or a play button are the kind of accidental likeness `brd:CRF-05` looks for. The kit names any resemblance it notices (`brd:LGL-02`).
- Searches the user can run: the USPTO trademark search system, including its image search (a beta launched in April 2026 that, per USPTO, supplements and does not replace a clearance search), and a professional clearance search before filing. Source: A16, snippet level. Checked 2026-11-18; recheck 2027-04-01. https://www.uspto.gov/subscription-center/2026/image-searching-powerful-tool-finding-similar-trademarks
- Secondary sources say the USPTO does not bar AI-generated marks, and the usual distinctiveness and likelihood-of-confusion tests apply (A16, secondary).

## Fonts and licences (brd:LGL-01, brd:TYP-02)

- Fonts under the SIL Open Font License may be used for logos without extra permission, and the graphic made from the outlines is the user's; renaming rules (Reserved Font Names) apply to modified fonts, not to a logo. Source: A12, OFL FAQ version 1.1-update8 (2026-11-09). Checked 2026-11-18; recheck 2027-05-01. https://openfontlicense.org/ofl-faq/
- Most Google Fonts families are OFL; a few are Apache or the Ubuntu Font Licence. Check each family's own licence file; the Ubuntu licence is outside `brd:TYP-02`'s OFL-or-Apache rule, so flag it for the user. Source: A13 (snippet level). Checked 2026-11-18; recheck 2027-05-01.
- Record the family, version and licence in the brief and on the brand sheet.

## Hosted generators (brd:LGL-03)

No hosted generator is used in v1. If one is added later, record the plan, who owns the output and any training-use clause. Example of why: one vendor's docs say free-plan outputs are public, owned by the vendor and not licensed for commercial use, while paid plans keep ownership and an upgrade is not retroactive. Source: Recraft ownership docs (track B, search-result summary). Checked 2026-11-18; recheck 2027-03-01. https://www.recraft.ai/docs/trust-and-security/ownership

## Wording for the brand sheet

The fill-in block is in `${CLAUDE_PLUGIN_ROOT}/templates/brand-sheet.md`. Keep its wording; add only the fonts, the tools and the provenance note.
