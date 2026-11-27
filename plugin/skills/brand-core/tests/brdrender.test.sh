#!/usr/bin/env bash
# Regression test for scripts/brdrender.py using a fake renderer (fixtures/bin/resvg).
# It proves the script's own logic (pre-check, PNG filters, mono and reversed, outputs);
# the last section runs against a real resvg or rsvg-convert when one is installed, and is skipped otherwise.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/brdrender.py"
FIX="$HERE/fixtures"
PY="$(command -v python3)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1
pass=0; fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL $1"; }

# no renderer: exit 3
PATH="" "$PY" -I "$SCRIPT" "$FIX/good.svg" >/dev/null 2>&1; [ $? -eq 3 ] && ok || bad "no renderer should exit 3"

REAL_PATH="$PATH"
export PATH="$FIX/bin:$PATH"
"$PY" -I "$SCRIPT" "$FIX/good.svg" >out.txt 2>&1; rc=$?
[ $rc -eq 0 ] && ok || { bad "good render exit $rc"; cat out.txt; }
for f in good-16 good-32 good-64 good-mono good-mono-inverted good-mirror good-rot90 good-rot180 good-display; do
  [ -s "brand/renders/$f.png" ] && ok || bad "missing $f.png"
done

[ ! -e brand/renders/good-reversed.png ] && ok || bad "good-reversed.png must not be written (name belongs to a real X-reversed.svg)"
"$PY" -I - <<'PY' && ok || bad "mono/reversed pixels"
import json, struct, sys, zlib
def gray(p):
    d = open(p, "rb").read(); pos = 8; idat = b""
    while pos < len(d):
        n, t = struct.unpack(">I4s", d[pos:pos+8]); b = d[pos+8:pos+8+n]; pos += 12 + n
        if t == b"IHDR": w, h, _, ct = struct.unpack(">IIBB", b[:10])
        if t == b"IDAT": idat += b
    assert ct == 0
    raw = zlib.decompress(idat)
    return w, h, [raw[y*(w+1)+1:(y+1)*(w+1)] for y in range(h)]
w, h, m = gray("brand/renders/good-mono.png")
_, _, r = gray("brand/renders/good-mono-inverted.png")
assert w == 256 and m[0][0] == 0 and m[0][w-1] == 255, "left black, right white"
assert all(a + b == 255 for x, y in zip(m, r) for a, b in zip(x, y)), "reversed is the inverse"
j = json.load(open("brand/renders/good-render.json"))
assert j["tools"]["resvg"] == "fake-resvg 0.0" and all(f["status"] == "review" and f["evidence"] == "render" for f in j["findings"])
PY

# a reversed or dark source renders its size PNGs and display PNG on a dark ground; probes and exports stay transparent
export BRD_FAKE_LOG="$WORK/fake.log"
for name in mark-reversed mark-dark.v2 dark; do
  cp "$FIX/good.svg" "$name.svg"; : > "$BRD_FAKE_LOG"
  "$PY" -I "$SCRIPT" "$name.svg" >/dev/null 2>&1
  n=$(grep -c -- "--background #1a1a1a" "$BRD_FAKE_LOG"); [ "$n" -eq 4 ] && ok || bad "$name: 3 sizes and the display render need a dark background (got $n)"
  grep -- "-w 256" "$BRD_FAKE_LOG" | grep -q -- "--background" && bad "$name: mono probe and variants must stay transparent" || ok
done
: > "$BRD_FAKE_LOG"; "$PY" -I "$SCRIPT" "$FIX/good.svg" >/dev/null 2>&1
grep -q -- "--background" "$BRD_FAKE_LOG" && bad "a light source must stay transparent" || ok
cp "$FIX/good.svg" undark.svg; : > "$BRD_FAKE_LOG"; "$PY" -I "$SCRIPT" undark.svg >/dev/null 2>&1
grep -q -- "--background" "$BRD_FAKE_LOG" && bad "undark is not a dark word" || ok
: > "$BRD_FAKE_LOG"; "$PY" -I "$SCRIPT" mark-reversed.svg --export --out brand/exp-rev >/dev/null 2>&1
grep -q -- "--background" "$BRD_FAKE_LOG" && bad "exports must stay transparent" || ok
unset BRD_FAKE_LOG

# printed paths are as given, never the resolved symlink target (brand/ itself is a link, for example to a synced folder)
rm -rf brand; mkdir -p linktarget && ln -s "$WORK/linktarget" brand
"$PY" -I "$SCRIPT" "$FIX/good.svg" >link.out 2>&1; rc=$?
[ $rc -eq 0 ] && grep -q "brand/renders/good-16.png" link.out && ! grep -q "linktarget" link.out && ok || { bad "paths must print as given (exit $rc)"; cat link.out; }
grep -q "linktarget" linktarget/renders/good-render.json && bad "the JSON must carry the paths as given too" || ok
[ -s linktarget/renders/good-16.png ] && ok || bad "render should still land in the link target"
rm brand; mkdir -p brand outside && ln -s "$WORK/outside" brand/escape
"$PY" -I "$SCRIPT" "$FIX/good.svg" --out brand/escape >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "a symlink pointing outside the root must still exit 2"
rm brand/escape

# --root: brand/ resolves against it
mkdir -p rootproj/brand && cp "$FIX/good.svg" rootproj/brand/mark.svg
"$PY" -I "$SCRIPT" brand/mark.svg --root rootproj >root.out 2>&1; rc=$?
[ $rc -eq 0 ] && [ -s rootproj/brand/renders/mark-16.png ] && ok || { bad "--root render (exit $rc)"; cat root.out; }
"$PY" -I "$SCRIPT" "$FIX/good.svg" --root "$FIX/good.svg" >root2.out 2>&1; [ $? -eq 2 ] && grep -q "not a directory" root2.out && ok || bad "--root that is not a directory should exit 2"

# pre-check blocks rendering: live text and external reference
rm -rf brand
for bad_svg in live-text external; do
  "$PY" -I "$SCRIPT" "$FIX/$bad_svg.svg" >/dev/null 2>&1; rc=$?
  [ $rc -eq 1 ] && [ ! -d brand/renders ] && ok || bad "$bad_svg should exit 1 and render nothing (exit $rc)"
done
# single-quoted viewBox must not crash the variants step
sed "s/viewBox=\"0 0 64 64\"/viewBox='0 0 64 64'/" "$FIX/good.svg" > sq.svg
"$PY" -I "$SCRIPT" sq.svg >sq.out 2>&1; rc=$?
[ $rc -eq 0 ] && ! grep -q Traceback sq.out && ok || { bad "single-quoted viewBox (exit $rc)"; cat sq.out; }
# hostile file is refused with exit 1 even when no renderer is installed
PATH="" "$PY" -I "$SCRIPT" "$FIX/two-causes.svg" >/dev/null 2>&1; [ $? -eq 1 ] && ok || bad "hostile file with no renderer should exit 1"
"$PY" -I "$SCRIPT" "$FIX/good.svg" --out /tmp/brdrender-escape >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "--out outside brand should exit 2"
"$PY" -I "$SCRIPT" "$FIX/nope.svg" >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "missing file should exit 2"

# real renderer (resvg or rsvg-convert), only when one is installed; the fake one is not on this PATH
if PATH="$REAL_PATH" command -v resvg >/dev/null 2>&1 || PATH="$REAL_PATH" command -v rsvg-convert >/dev/null 2>&1; then
  rm -rf brand
  PATH="$REAL_PATH" "$PY" -I "$SCRIPT" "$FIX/good.svg" >real.out 2>&1; rc=$?
  [ $rc -eq 0 ] && ok || { bad "real renderer exit $rc"; cat real.out; }
  PATH="$REAL_PATH" "$PY" -I - <<'PY' && ok || bad "real renderer output"
import json, struct, zlib
def png(p):
    d = open(p, "rb").read(); assert d[:8] == b"\x89PNG\r\n\x1a\n", p
    pos = 8; idat = b""
    while pos < len(d):
        n, t = struct.unpack(">I4s", d[pos:pos+8]); b = d[pos+8:pos+8+n]; pos += 12 + n
        if t == b"IHDR": w, h, _, ct = struct.unpack(">IIBB", b[:10])
        if t == b"IDAT": idat += b
    return w, h, ct, zlib.decompress(idat)
for name, width in (("16", 16), ("32", 32), ("64", 64), ("display", 512)):
    assert png("brand/renders/good-%s.png" % name)[0] == width, name
w, h, ct, mono = png("brand/renders/good-mono.png")
_, _, _, rev = png("brand/renders/good-mono-inverted.png")
assert ct == 0 and w == 256
rows = lambda raw: [raw[y*(w+1)+1:(y+1)*(w+1)] for y in range(h)]
m, r = rows(mono), rows(rev)
assert {v for row in m for v in row} <= {0, 255}, "mono must be only black and white"
assert all(a + b == 255 for x, y in zip(m, r) for a, b in zip(x, y)), "reversed is the inverse"
assert any(0 in row for row in m) and any(255 in row for row in m), "mono has both colours"
j = json.load(open("brand/renders/good-render.json"))
assert any(j["tools"].values()) and "fake" not in json.dumps(j["tools"]), j["tools"]
PY
  # export mode: SVG copy, transparent PNGs, manifest; a background fails unless the file is a tile
  PATH="$REAL_PATH" "$PY" -I "$SCRIPT" "$FIX/good.svg" --export >exp.out 2>&1; rc=$?
  cp "$FIX/good.svg" mark-reversed.svg
  PATH="$REAL_PATH" "$PY" -I "$SCRIPT" mark-reversed.svg --sizes 16 --out brand/realrev >realrev.out 2>&1; rc=$?
  PATH="$REAL_PATH" BRD_SCRIPTS="$HERE/../scripts" "$PY" -I - <<'PY' && ok || bad "real renderer: a reversed source should render on an opaque dark ground"
import os, sys
sys.path.insert(0, os.environ["BRD_SCRIPTS"])
import brdcheck
assert brdcheck.opaque_ratio("brand/realrev/mark-reversed-16.png") == 1.0
assert brdcheck.opaque_ratio("brand/realrev/mark-reversed-display.png") == 1.0
PY
  [ $rc -eq 0 ] && grep -q "transparent: yes" exp.out && ok || { bad "export of a transparent file (exit $rc)"; cat exp.out; }
  missing=0; for f in svg/good.svg png/good-16.png png/good-1024.png manifest.json; do [ -s "brand/exports/$f" ] || missing=1; done
  [ $missing -eq 0 ] && ok || bad "export files missing"
  PATH="$REAL_PATH" "$PY" -I "$SCRIPT" "$FIX/ground.svg" --export --out brand/exports-opaque >expg.out 2>&1; rc=$?
  [ $rc -eq 1 ] && grep -q "brd:CTR-06" expg.out && ok || { bad "an export with a background should exit 1 with brd:CTR-06 (exit $rc)"; cat expg.out; }
  cp "$FIX/ground.svg" ground-tile.svg
  PATH="$REAL_PATH" "$PY" -I "$SCRIPT" ground-tile.svg --export >expt.out 2>&1; rc=$?
  [ $rc -eq 0 ] && ok || { bad "a tile may keep its background (exit $rc)"; cat expt.out; }
  grep -q '"tile": true' brand/exports/manifest.json && ok || bad "tile not recorded in the manifest"
  (cd brand/exports && "$PY" -I -m zipfile -c assets.zip svg png) && "$PY" -I "$HERE/../scripts/brdcheck.py" --exports brand/exports >expc.out 2>&1
  grep -q "brd:CTR-06" expc.out && { bad "brdcheck rejected a real export set"; cat expc.out; } || ok
else
  echo "brdrender tests: no real renderer installed, real-renderer tests skipped"
fi

echo "brdrender tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
