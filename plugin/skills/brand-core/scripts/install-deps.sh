#!/usr/bin/env bash
# install-deps: check for, or install, the optional tools the brd scripts use.
#   install-deps.sh --check [--data DIR]   list each tool as ok or missing; exit 3 if any is missing
#   install-deps.sh --data DIR             install what is missing; prints every command before it runs
# DIR is the plugin data folder (the skills pass ${CLAUDE_PLUGIN_DATA}); the Python packages go in DIR/venv,
# never in the user's global Python. Nothing is installed without the user saying yes first (the skill asks).
set -u
FONTTOOLS="fonttools==4.68.0"
UHARFBUZZ="uharfbuzz==0.57.0"
mode=install data="${CLAUDE_PLUGIN_DATA:-}"
while [ $# -gt 0 ]; do
  case "$1" in
    --check) mode=check ;;
    --data) [ $# -ge 2 ] || { echo "install-deps: --data needs a folder" >&2; exit 2; }; data="$2"; shift ;;
    -h|--help) sed -n 2,6p "$0"; exit 0 ;;
    *) echo "install-deps: unknown argument $1" >&2; exit 2 ;;
  esac
  shift
done
[ "$mode" = check ] || [ -n "$data" ] || { echo "install-deps: --data DIR is required to install (the Python venv goes there)" >&2; exit 2; }

py() { if [ -n "$data" ] && [ -x "$data/venv/bin/python" ]; then echo "$data/venv/bin/python"; else echo python3; fi; }
has_mod() { "$(py)" -c "import $1" 2>/dev/null; }
renderer() { command -v resvg >/dev/null && { echo resvg; return; }; command -v rsvg-convert >/dev/null && echo rsvg-convert; }
run() { echo "+ $*"; "$@"; }

report() {
  missing=0
  if r=$(renderer) && [ -n "$r" ]; then echo "ok      renderer: $r"
  else echo "missing renderer (resvg or rsvg-convert): renders and PNG exports; render rules stay review, verdict incomplete"; missing=1; fi
  if has_mod fontTools; then echo "ok      fontTools ($(py))"
  else echo "missing fontTools: wordmark outlines and glyph coverage (brdtext); you supply the outlined wordmark"; missing=1; fi
  if has_mod uharfbuzz; then echo "ok      uharfbuzz ($(py))"
  else echo "missing uharfbuzz (optional): full kerning and non-Latin shaping; pair kerning from the font still applies"; missing=1; fi
  if command -v svgo >/dev/null; then echo "ok      svgo (optional)"
  else echo "skip    svgo (optional optimiser, not installed by this script): npm install -g svgo"; fi
  return $missing
}

if [ "$mode" = check ]; then report && exit 0; exit 3; fi

if [ -z "$(renderer)" ]; then
  if command -v brew >/dev/null; then run brew install resvg
  elif command -v apt-get >/dev/null; then
    if [ "$(id -u)" -eq 0 ]; then run apt-get install -y librsvg2-bin
    elif sudo -n true 2>/dev/null; then run sudo apt-get install -y librsvg2-bin
    else echo "install-deps: needs your password; run this yourself: sudo apt-get install -y librsvg2-bin"; fi
  elif command -v dnf >/dev/null; then echo "install-deps: run this yourself: sudo dnf install -y librsvg2-tools"
  else echo "install-deps: no known package manager; install resvg from https://github.com/linebender/resvg/releases"; fi
fi

if ! has_mod fontTools || ! has_mod uharfbuzz; then
  command -v python3 >/dev/null || { echo "install-deps: python3 not found; install Python 3 first" >&2; exit 3; }
  [ -x "$data/venv/bin/python" ] || { mkdir -p "$data" && run python3 -m venv "$data/venv"; } || { echo "install-deps: could not create $data/venv" >&2; exit 3; }
  run "$data/venv/bin/python" -m pip install --quiet --disable-pip-version-check "$FONTTOOLS" || echo "install-deps: fontTools install failed"
  # uharfbuzz is optional; a platform without a wheel keeps pair kerning from fontTools
  run "$data/venv/bin/python" -m pip install --quiet --disable-pip-version-check "$UHARFBUZZ" || echo "install-deps: uharfbuzz install failed (optional)"
fi

echo; report && exit 0; exit 3
