#!/usr/bin/env bash
# Regression test for scripts/brdtext.py. Needs fontTools to build a tiny test font;
# without it only the exit-3 path is checked. Set BRD_PYTHON to a python that has fontTools (and uharfbuzz).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/brdtext.py"
PY="${BRD_PYTHON:-python3}"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1
pass=0; fail=0
ok() { pass=$((pass+1)); }
bad() { fail=$((fail+1)); echo "FAIL $1"; }

if ! "$PY" -c "import fontTools" 2>/dev/null; then
  : > x.ttf
  "$PY" -I "$SCRIPT" --font x.ttf --text A --out brand/x.svg >x.out 2>&1; [ $? -eq 3 ] && grep -q "pip install fonttools uharfbuzz" x.out && ok || bad "missing fontTools: exit 3 naming pip install fonttools uharfbuzz"
  # exit 2 (no font) or 3 (no fontTools) are both acceptable before the font is read; fontTools check comes after the font check
  echo "brdtext tests: fontTools not installed, build-and-compare tests skipped"
  echo "brdtext tests: $pass passed, $fail failed (skipped)"
  [ "$fail" -eq 0 ]; exit $?
fi

# Build a tiny font: glyphs A and V (triangles), a legacy kern pair A,V = -100, licence name records.
"$PY" - <<'PY'
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._k_e_r_n import KernTable_format_0
fb = FontBuilder(1000, isTTF=True)
fb.setupGlyphOrder([".notdef", "space", "A", "V"])
fb.setupCharacterMap({32: "space", 65: "A", 86: "V"})
def tri():
    p = TTGlyphPen(None); p.moveTo((0, 0)); p.lineTo((300, 700)); p.lineTo((600, 0)); p.closePath(); return p.glyph()
empty = TTGlyphPen(None).glyph()
fb.setupGlyf({".notdef": empty, "space": empty, "A": tri(), "V": tri()})
fb.setupHorizontalMetrics({g: (650, 0) for g in [".notdef", "space", "A", "V"]})
fb.setupHorizontalHeader(ascent=800, descent=-200)
fb.setupNameTable({"familyName": "Testface", "styleName": "Regular", "licenseDescription": "Test licence text -- OFL", "licenseInfoURL": "https://example.invalid/ofl"})
fb.setupOS2(); fb.setupPost()
k = newTable("kern"); k.version = 0
t = KernTable_format_0(); t.version = 0; t.coverage = 1; t.format = 0; t.kernTable = {("A", "V"): -100}
k.kernTables = [t]
fb.font["kern"] = k
fb.save("test.ttf")
PY

run() { "$PY" -I "$SCRIPT" --font test.ttf --text "$1" --size 100 --out "brand/$2.svg" "${@:3}" >"$2.out" 2>&1; }

run AV kerned --no-harfbuzz && ok || { bad "kerned run"; cat kerned.out; }
run AV nokern --no-harfbuzz --tracking 0 >/dev/null
# Reference without kerning: same text with letters in an order that has no pair (VA)
run VA plain --no-harfbuzz && ok || bad "plain run"

"$PY" -I - <<'PY' && ok || bad "svg contents"
import re, json
s = open("brand/kerned.svg").read()
assert "<text" not in s and "<title>" in s and 'id="wordmark"' in s
assert len(re.findall(r'<path id="glyph-', s)) == 2
assert "Testface" in s and "shaping=none" in s
j = json.load(open("brand/kerned.json"))
assert j["font"]["family"] == "Testface" and j["font"]["shaping"] == "none"
assert any(f["id"] == "brd:TYP-02" and f["status"] == "review" and "OFL" in f["finding"] for f in j["findings"])
# kerning applied: AV is 100 units (10 px at size 100 / 1000 upm) tighter than VA
wk = float(re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+)', open("brand/kerned.svg").read()).group(1))
wp = float(re.search(r'viewBox="[-\d.]+ [-\d.]+ ([\d.]+)', open("brand/plain.svg").read()).group(1))
assert abs((wp - wk) - 10) < 0.05, (wk, wp)
# decimals: no number with more than 2 decimals in path data
assert not re.search(r"\d\.\d{3}", re.sub(r'<!--.*?-->', '', s, flags=re.S))
PY

# generated output passes brdcheck (no live text, in viewBox)
"$PY" -I "$HERE/../scripts/brdcheck.py" brand/kerned.svg >chk.out 2>&1; rc=$?
[ $rc -eq 0 ] && ok || { bad "brdcheck on wordmark (exit $rc)"; cat chk.out; }

run "Ж" cyr --no-harfbuzz; [ $? -eq 3 ] && ok || bad "non-Latin without shaping should exit 3"
run Q noglyph --no-harfbuzz; [ $? -eq 2 ] && ok || bad "missing glyph should exit 2"
grep -q "brd:TYP-07" noglyph.out && ok || bad "missing glyph should cite brd:TYP-07"
grep -q '"brd:TYP-07"' brand/kerned.json && ok || bad "TYP-07 pass missing from the JSON record"
run AV wtstatic --no-harfbuzz --weight 700; [ $? -eq 2 ] && ok || bad "--weight on a static font should exit 2"
"$PY" -I "$SCRIPT" --font test.ttf --text AV --out /tmp/brdtext-escape.svg >/dev/null 2>&1; [ $? -eq 2 ] && ok || bad "--out outside brand should exit 2"

# --root: brand/ resolves against it; a non-directory exits 2
mkdir -p rootproj && cp test.ttf rootproj/
"$PY" -I "$SCRIPT" --font test.ttf --text AV --no-harfbuzz --root rootproj >root.out 2>&1; rc=$?
[ $rc -eq 0 ] && [ -s rootproj/brand/wordmark.svg ] && ok || { bad "--root run (exit $rc)"; cat root.out; }
"$PY" -I "$SCRIPT" --font test.ttf --text AV --root test.ttf >root2.out 2>&1; [ $? -eq 2 ] && grep -q "not a directory" root2.out && ok || bad "--root that is not a directory should exit 2"

# no uharfbuzz: a review line says kerning was not applied and to install it
grep -q "brd:TYP-03 review: kerning from uharfbuzz was not applied" kerned.out && grep -q "install uharfbuzz" kerned.out && ok || bad "shaping none should print a review line naming uharfbuzz"
grep -q "pip install uharfbuzz" <(python3 -c "import json;print(json.load(open('brand/kerned.json'))['findings'])") && ok || bad "the review line should be in the JSON record"

# fontTools missing: exit 3 naming both packages (the import probe is faked, so this runs wherever the test does)
: > nofont.ttf
"$PY" -I - "$SCRIPT" nofont.ttf >nofonttools.out 2>&1 <<'PY'
import importlib.util, runpy, sys
real = importlib.util.find_spec
importlib.util.find_spec = lambda n, *a: None if n == "fontTools" else real(n, *a)
sys.argv = [sys.argv[1], "--font", sys.argv[2], "--text", "A", "--out", "brand/nf.svg"]
runpy.run_path(sys.argv[0], run_name="__main__")
PY
[ $? -eq 3 ] && grep -q "pip install fonttools uharfbuzz" nofonttools.out && ok || { bad "missing fontTools: exit 3 naming pip install fonttools uharfbuzz"; cat nofonttools.out; }

# --opsz: a variable font with wght and opsz axes (the right foot of A moves 100 units across the opsz range)
"$PY" - <<'PY'
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables.TupleVariation import TupleVariation
fb = FontBuilder(1000, isTTF=True)
order = [".notdef", "space", "A", "V"]
fb.setupGlyphOrder(order)
fb.setupCharacterMap({32: "space", 65: "A", 86: "V"})
def tri():
    p = TTGlyphPen(None); p.moveTo((0, 0)); p.lineTo((300, 700)); p.lineTo((600, 0)); p.closePath(); return p.glyph()
empty = TTGlyphPen(None).glyph()
fb.setupGlyf({".notdef": empty, "space": empty, "A": tri(), "V": tri()})
fb.setupHorizontalMetrics({g: (650, 0) for g in order})
fb.setupHorizontalHeader(ascent=800, descent=-200)
fb.setupNameTable({"familyName": "Varface", "styleName": "Regular"})
fb.setupOS2(); fb.setupPost()
fb.setupFvar([("wght", 100, 400, 900, "Weight"), ("opsz", 8, 14, 144, "Optical size")], [])
fb.setupGvar({"A": [TupleVariation({"opsz": (0, 1, 1)}, [(0, 0), (0, 0), (100, 0), (0, 0), (0, 0), (0, 0), (0, 0)])]})
fb.save("var.ttf")
PY
vrun() { "$PY" -I "$SCRIPT" --font var.ttf --text A --size 100 --no-harfbuzz --out "brand/$1.svg" "${@:2}" >"$1.out" 2>&1; }
width() { sed -n 's/.*viewBox="[-0-9.]* [-0-9.]* \([0-9.]*\).*/\1/p' "brand/$1.svg" | head -1; }
vrun o14 && vrun o144 --opsz 144 && vrun o999 --opsz 999 && vrun o4 --opsz 4 && vrun o8 --opsz 8 && ok || { bad "opsz runs"; cat o999.out; }
[ "$(width o144)" = "70" ] && [ "$(width o14)" != "70" ] && ok || bad "--opsz 144 should widen A (got $(width o144), default $(width o14))"
[ "$(width o999)" = "70" ] && grep -q "outside the font's optical-size range 8 to 144; clamped to 144" o999.out && ok || bad "--opsz 999 should clamp to 144 and say so"
[ "$(width o4)" = "$(width o8)" ] && grep -q "clamped to 8" o4.out && ok || bad "--opsz 4 should clamp to 8 and say so"
grep -q "clamped" o144.out && bad "an in-range --opsz must not report a clamp" || ok
grep -q '"opsz": 144' brand/o999.json && ok || bad "the record should hold the opsz used"
vrun o70w --opsz 144 --weight 700 && [ "$(width o70w)" = "70" ] && ok || bad "--opsz with --weight"
run AV opsz-static --no-harfbuzz --opsz 20; [ $? -eq 0 ] && grep -q "ignored: the font has no optical-size axis" opsz-static.out && ok || bad "--opsz on a static font should be reported and ignored"

if "$PY" -c "import uharfbuzz" 2>/dev/null; then
  run AV hb && ok || { bad "harfbuzz run"; cat hb.out; }
  grep -q "shaping=uharfbuzz" brand/hb.svg && ok || bad "harfbuzz shaping not recorded"
  run Q hbnoglyph; [ $? -eq 2 ] && grep -q "brd:TYP-07" hbnoglyph.out && ok || bad "harfbuzz: missing glyph should exit 2 with brd:TYP-07, not draw .notdef"
else
  echo "uharfbuzz not installed: shaping path skipped"
fi

echo "brdtext tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
