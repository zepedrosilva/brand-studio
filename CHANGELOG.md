# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the plugin uses [semantic versioning](https://semver.org/). A release is a change to `plugin/.claude-plugin/plugin.json`'s `version`; installed copies update only when it rises.

## [Unreleased]

## [0.5.3] - 2026-11-28

### Fixed

- `brdrender.py` renders a file inside `brand/concepts/<x>/` into that concept's own `renders/` folder by default. All three concept files are named `concept.svg`, so renders that fell back to the shared `brand/renders/` overwrote each other, the name test and render rules could judge one concept's images as another's, and the live page, which reads each concept's own folder, showed no renders. The designer and reviewer instructions no longer pass `--out` for concepts ([#1](https://github.com/zepedrosilva/brand-studio/issues/1)).
- The own-word question on the live page explains the term, with an example, before the suggested answer ([#2](https://github.com/zepedrosilva/brand-studio/issues/2)).

## [0.5.2] - 2026-11-27

### Fixed

- The author name is written with its accent: José Silva.

## [0.5.1] - 2026-11-27

### Fixed

- The plugin homepage points at the new site address, zepedro.com/plugins/brand-studio/.

## [0.5.0] - 2026-11-27

First public release. Five private iterations (0.1.0 to 0.4.0, 2026-11-18 to 2026-11-19) were folded into this one.

### Added

- `brand-core` skill: eight principles, the `brd` rule catalogue in twelve families (DEC, CNC, CTR, CAP, CRF, TYP, SET, SEC, EVD, LGL, PAL, POS), severities, statuses, evidence levels and source labels, the brief declaration, thresholds, legal notes (US-centred, warnings only), and colour, type and positioning references.
- `brand-create` skill: narrative to brief, a metaphor shortlist, three greyscale concepts drawn in parallel, one checkpoint with a recommendation, then the kit (variants, palette roles with OKLCH ramps, outlined wordmark, lockups, optional icon set, brand sheet), at scope A, B or C. It runs a live page on 127.0.0.1 that becomes the final brand design brief.
- `brand-review` skill: SVG review with rule IDs and an evidence level per finding; vision-only, provisional review for PNG or JPG.
- `brand-designer` and `brand-reviewer` agents on different models, so the reviewer does not grade its own work.
- Optional scripts: `brdcheck` (deterministic SVG checks), `brdrender` (renders and the export set), `brdtext` (shaped, kerned wordmark outlines), `brdinuse` (the kit placed in applications, every colour pair measured) and `brdlive` (the live page). Python 3 standard library, except `brdtext`, which needs `fontTools`.
- `install-deps.sh` and a tool check at the start of `/brand-create` and `/brand-review`: missing tools are listed, the user is asked once whether to install them (the renderer through the system package manager, `fontTools` and `uharfbuzz` in a private venv under the plugin's data folder), and the run degrades to `judgment` evidence only on a no.
- `brd:CNC-03`, the name test: a reviewer guesses what each mark means with no text beside it. Added after a full run in which abstract concepts passed every check and still meant nothing next to the name.
- Research behind every rule and number: `plugin/research/`, 81 cited sources with check and recheck dates.
