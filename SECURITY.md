# Security policy

## Supported versions

Only the latest release receives fixes.

## Reporting a vulnerability

Report privately through [GitHub security advisories](https://github.com/zepedrosilva/brand-studio/security/advisories/new). Do not open a public issue. Expect a first reply within a week. Once a fix is released, the advisory is published with credit unless you prefer otherwise.

## What is in scope

brand-studio runs on your machine, inside Claude Code. The parts that handle untrusted input or open a port are the ones to look at:

- **SVG parsing.** The scripts in `plugin/skills/brand-core/scripts/` read SVG files that may come from anyone. They parse them as data only: never executed, never opened in a browser, and no external reference is fetched. Files with `<!DOCTYPE` or `<!ENTITY` declarations are refused (`brd:SEC-01`). A way to make a script execute, fetch or write outside `brand/` is a vulnerability.
- **The live page.** `brdlive.py` serves `brand/index.html` on 127.0.0.1 only, with a per-run token and an origin check, while `/brand-create` runs. A way to reach it from another origin or host, or to read files outside `brand/`, is a vulnerability.
- **Output paths.** Every script refuses to write outside the `brand/` folder of the project. A path that escapes it is a vulnerability.

Out of scope: what the model draws or writes (report it as a bug), and the optional third-party tools (`resvg`, `rsvg-convert`, `fontTools`, `uharfbuzz`, `svgo`); report those upstream.

## Repository hooks

This repository ships two Claude Code hooks in `.claude/settings.json` for contributors. They run only after you trust the folder, only read files, never block a prompt and never use the network. See [CONTRIBUTING.md](CONTRIBUTING.md).
