---
status: accepted
date: 2026-11-27
---

<!-- Based on the MADR 4.0.0 minimal template (MIT or CC0), headings in sentence case. -->

# Ask to install missing tools, degrade only when the user declines

Amends [0005](0005-optional-standard-library-scripts.md): the scripts stay optional, but a missing tool is no longer only a hint at the end of a run.

## Context and problem statement

Without a renderer and fontTools, render rules stay `review`, the verdict is `incomplete` and the user has to outline the wordmark by hand. The dogfood run found the missing tools halfway through `/brand-create`, and the only help was a one-line hint. How should the plugin get the tools a run needs without forcing an install?

## Considered options

- Report missing tools and never install (the 0005 behaviour)
- Check at the start, ask once, install on yes with a bundled script, degrade on no
- Require the tools and stop without them

## Decision outcome

Chosen option: check, ask, install on yes and degrade on no. The skills run `install-deps.sh --check` before the first script. If something is missing, they ask once, recommending the install. On yes, `install-deps.sh` installs the renderer with the system package manager and puts `fontTools` and `uharfbuzz` (pinned) in a private venv under `${CLAUDE_PLUGIN_DATA}`. On no, the run carries on at `judgment` level as before. `svgo` is reported but not installed, because it would need a global npm install.

### Consequences

- Good, because most runs reach `script` and `render` evidence without the user researching packages.
- Good, because nothing is installed without a yes, and the user's global Python is never touched.
- Good, because the README and CONTRIBUTING point to the same script, so there is one install path.
- Bad, because the plugin now ships a shell script that runs package managers; it prints every command first, and a command that needs a password is handed back to the user.
- Bad, because `brdtext.py` now has two possible interpreters, the venv and `python3`.
