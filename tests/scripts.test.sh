#!/bin/bash
# Self-checks for scripts/check-version.sh in a throwaway repo.
set -u
here=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cd "$tmp" && git init -q && git config user.email t@example.com && git config user.name t
mkdir -p plugin/.claude-plugin && echo '{ "version": "0.5.0" }' > plugin/.claude-plugin/plugin.json
echo a > plugin/a && git add -A && git commit -qm base && git tag base
fails=0
ok() { if "$@" >/dev/null 2>&1; then echo "ok: $*"; else echo "FAIL: $*"; fails=1; fi; }
no() { if "$@" >/dev/null 2>&1; then echo "FAIL (should fail): $*"; fails=1; else echo "ok (fails): $*"; fi; }
ok sh "$here/scripts/check-version.sh" base
echo b > plugin/a; git commit -qam change
no sh "$here/scripts/check-version.sh" base
echo '{ "version": "0.10.0" }' > plugin/.claude-plugin/plugin.json; git commit -qam bump
ok sh "$here/scripts/check-version.sh" base
echo '{ "version": "0.4.9" }' > plugin/.claude-plugin/plugin.json; git commit -qam down
no sh "$here/scripts/check-version.sh" base
exit $fails
