#!/usr/bin/env bash
# Regression test for scripts/install-deps.sh. Uses stub tools on a private PATH; never installs anything.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/install-deps.sh"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
pass=0; fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL $1"; }

# A PATH with only the basics: no renderer, no svgo, and a python3 that has no packages.
mkdir -p "$WORK/bin" "$WORK/data/venv/bin"
for t in sed id mkdir; do ln -s "$(command -v $t)" "$WORK/bin/$t"; done
printf '#!/bin/sh\nexit 1\n' > "$WORK/bin/python3"; chmod +x "$WORK/bin/python3"
BASH_BIN="$(command -v bash)"
run() { env -i PATH="$WORK/bin" "$BASH_BIN" "$SCRIPT" "$@"; }

out=$(run --check 2>&1); rc=$?
[ $rc -eq 3 ] && ok || bad "--check with nothing installed should exit 3, got $rc"
echo "$out" | grep -q "missing renderer" && ok || bad "--check should name the missing renderer"
echo "$out" | grep -q "missing fontTools" && ok || bad "--check should name missing fontTools"

run --bogus >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "unknown argument should exit 2"
run >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "install without --data should exit 2"

# Everything present: a stub renderer, and a venv python whose imports succeed.
printf '#!/bin/sh\nexit 0\n' > "$WORK/bin/resvg"; chmod +x "$WORK/bin/resvg"
printf '#!/bin/sh\nexit 0\n' > "$WORK/data/venv/bin/python"; chmod +x "$WORK/data/venv/bin/python"
out=$(run --check --data "$WORK/data" 2>&1); rc=$?
[ $rc -eq 0 ] && ok || { bad "--check with everything present should exit 0, got $rc"; echo "$out"; }
echo "$out" | grep -q "ok      fontTools ($WORK/data/venv/bin/python)" && ok || bad "--check should prefer the venv python"

# Install with everything present runs no install command.
out=$(run --data "$WORK/data" 2>&1); rc=$?
[ $rc -eq 0 ] && ! echo "$out" | grep -q '^+ ' && ok || { bad "install with nothing missing should run nothing"; echo "$out"; }

echo "install-deps tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
