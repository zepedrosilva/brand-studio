#!/bin/sh
# Fails when plugin/ changed since <base> but plugin.json's version did not rise.
# plugin/research/ is documentation only and needs no bump.
# Usage: sh scripts/check-version.sh <base-ref>
set -eu
base=${1:?usage: check-version.sh <base-ref>}
manifest=plugin/.claude-plugin/plugin.json
git rev-parse --verify --quiet "$base^{commit}" >/dev/null || { echo "base ref not found: $base"; exit 2; }
if git diff --quiet "$base" -- plugin/ ':(exclude)plugin/research/'; then echo "plugin/ unchanged (research/ aside): no bump needed"; exit 0; fi
ver() { sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1; }
old=$(git show "$base:$manifest" 2>/dev/null | ver || true)
new=$(ver < "$manifest")
[ -n "$old" ] || { echo "no version at $base: treating $new as the first release"; exit 0; }
# Highest of the two by version sort; it must be the new one and differ from the old.
top=$(printf '%s\n%s\n' "$old" "$new" | sort -t. -k1,1n -k2,2n -k3,3n | tail -n1)
if [ "$new" != "$old" ] && [ "$top" = "$new" ]; then echo "version $old -> $new"; exit 0; fi
echo "plugin/ changed but version did not rise ($old -> $new): bump it in $manifest (docs/authoring.md)"
exit 1
