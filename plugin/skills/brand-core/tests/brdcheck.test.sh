#!/usr/bin/env bash
# Regression test for scripts/brdcheck.py. Run: bash tests/brdcheck.test.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/brdcheck.py"
FIX="$HERE/fixtures"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1
pass=0; fail=0

# run <name> <expected exit> <expected id-or-empty> <args...>
run() {
  local name="$1" code="$2" id="$3"; shift 3
  out="$(python3 -I "$SCRIPT" "$@" 2>&1)"; rc=$?
  ok=1
  [ "$rc" -eq "$code" ] || ok=0
  if [ -n "$id" ]; then echo "$out" | grep -q "$id" || ok=0; fi
  if [ "$ok" -eq 1 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $name (exit $rc, want $code, id '$id')"; echo "$out" | head -5; fi
}
absent() { # absent <name> <id> <args...>: the id must NOT appear
  local name="$1" id="$2"; shift 2
  out="$(python3 -I "$SCRIPT" "$@" 2>&1)"
  if echo "$out" | grep -q "$id"; then fail=$((fail+1)); echo "FAIL $name: $id should not appear"; else pass=$((pass+1)); fi
}

run good 0 "" "$FIX/good.svg" --grid-unit 4
absent good-no-must "^fail " "$FIX/good.svg" --grid-unit 4
run live-text 1 "brd:CTR-04" "$FIX/live-text.svg"
run live-text-typ01 1 "brd:TYP-01" "$FIX/live-text.svg"
run many-colours 0 "brd:CAP-01" "$FIX/many-colours.svg"
run script-owned-by-sec 1 "brd:SEC-01" "$FIX/script.svg"
absent script-not-ctr02 "brd:CTR-02" "$FIX/script.svg"
run no-viewbox 1 "brd:CTR-01" "$FIX/no-viewbox.svg"
run doctype-is-sec01 1 "brd:SEC-01" "$FIX/doctype.svg"
run near-angle 0 "brd:CRF-03" "$FIX/near-angle.svg" --grid-unit 4
run gradient-no-flat 0 "brd:CTR-05" "$FIX/gradient.svg"
run outside-viewbox 1 "brd:CTR-01" "$FIX/outside.svg"
run prose-around 1 "brd:CTR-01" "$FIX/prose.svg"
run external-ref 1 "brd:CTR-04" "$FIX/external.svg"
run contrast-text 0 "brd:EVD-02" --brief "$FIX/brief-lowcontrast.md"
run waiver 0 "waived" "$FIX/many-colours.svg" --brief "$FIX/brief-waiver.md"
run arc-bounds 0 "padding left=8.00 top=8.00" "$FIX/arc.svg"
run style-import 1 "brd:CTR-04" "$FIX/style-import.svg"
run sec01-all-causes 1 "<script>, event handler" "$FIX/two-causes.svg"
run icons-safety 1 "brd:TYP-01" --icons "$FIX/icons-bad"
run dir-recursive 1 "x.svg" "$FIX/nested"
run wordmark-font-empty 1 "wordmark-font is empty" "$FIX/wordmark-live.svg" --stage kit --brief "$FIX/brief-nofont.md"
run stroke-in-bounds 0 "padding left=16.00 top=12.00 right=8.00" "$FIX/stroke.svg"
absent ground-not-ink "padding left=0.00" "$FIX/ground.svg"
absent centred-silent "brd:CRF-04" "$FIX/centred.svg"
absent glyph-not-grid "brd:CRF-03" "$FIX/wordmark-glyph.svg" --grid-unit 4
absent scaled-group-keeps-grid "brd:CRF-03" "$FIX/scaled.svg" --grid-unit 8
absent percent-size-in-bounds "extends outside the viewBox" "$FIX/pct.svg"
run style-overrides-stroke-attr 0 "padding left=16.00 top=12.00 right=8.00" "$FIX/style-stroke.svg"
absent nonuniform-scale-keeps-grid "brd:CRF-03" "$FIX/nonuniform.svg" --grid-unit 8
run palette-no-background 0 "no background colour" "$FIX/good.svg" --brief "$FIX/brief-nobg.md"
run fake-lettering-flagged 0 "brd:CRF-03" "$FIX/mark-fake.svg" --grid-unit 4
run rotated-rect-bounds 1 "extends outside the viewBox" "$FIX/rot-rect.svg"
run scaled-skip-still-flags-unscaled 0 "brd:CRF-03" "$FIX/scaled-off.svg" --grid-unit 8
run palette-not-run 0 "n/a" "$FIX/good.svg" --brief "$FIX/brief-nopalette.md"
run merged-line 1 "brd:CTR-04, brd:TYP-01" "$FIX/live-text.svg"
run missing-file 2 "no such file" "$FIX/nope.svg"
run out-outside-brand 2 "brand folder" "$FIX/good.svg" --out /tmp/brdcheck-escape.json

# palette roles, colour-blind distance, positioning
python3 -I - "$SCRIPT" <<'PY' && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL colour maths"; }
import importlib.util, sys
sp = importlib.util.spec_from_file_location("b", sys.argv[1]); b = importlib.util.module_from_spec(sp); sp.loader.exec_module(b)
w, r = b.oklab("#ffffff"), b.oklab("#ff0000")
assert all(abs(x - y) < 1e-3 for x, y in zip(w, (1.0, 0.0, 0.0))), w                      # white is (1, 0, 0)
assert all(abs(x - y) < 1e-3 for x, y in zip(r, (0.628, 0.2249, 0.1258))), r             # red, Ottosson's published values
for kind, m in b.CVD.items():
    assert all(abs(sum(row) - 1.0) < 1e-3 for row in m), kind                                # rows sum to 1: greys stay grey
assert b.ok_dist(b.cvd_oklab("#808080", "deuteranopia"), b.oklab("#808080")) < 1e-3          # a grey is unchanged
PY
run roles-good 0 "" --brief "$FIX/brief-roles-good.md"
absent roles-good-no-fail "^fail " --brief "$FIX/brief-roles-good.md"
run roles-incomplete 0 "brd:PAL-01" --brief "$FIX/brief-roles-incomplete.md"
run roles-too-many-hues 0 "brd:PAL-02" --brief "$FIX/brief-roles-bad.md"
run roles-text-contrast 0 "light text #8a9ba5 on background" --brief "$FIX/brief-roles-bad.md"
run roles-deutan-alike 0 "under deuteranopia simulation" --brief "$FIX/brief-roles-bad.md"
run positioning-missing 0 "brd:POS-01" --brief "$FIX/brief-roles-bad.md"
run rationale-missing-lines 0 "has no line for: warm, palette, type" --brief "$FIX/brief-roles-bad.md"
run ramp-out-of-order 0 "brd:PAL-03" --brief "$FIX/brief-roles-ramp.md"
run break-colour-too-near 0 "brd:PAL-07" --brief "$FIX/brief-roles-cat.md"
absent break-colour-far "brd:PAL-07" --brief "$FIX/brief-roles-good.md"
run unknown-role 0 "unknown role" --brief "$FIX/brief-roles-bad.md"
absent positioning-complete "brd:POS-0" --brief "$FIX/brief-roles-good.md"
run positioning-n-a 0 "n/a brd:POS-01" --brief "$FIX/brief-nopalette.md"

# PAL-08: variant colours against the declared roles
run variant-stray-colour 0 "brd:PAL-08" "$FIX/stray-colour.svg" --brief "$FIX/brief-roles-good.md"
absent variant-role-colour "brd:PAL-08" "$FIX/role-colour.svg" --brief "$FIX/brief-roles-good.md"
run variant-light-uses-dark 0 "light file uses dark-column" "$FIX/wrong-column.svg" --brief "$FIX/brief-roles-good.md"
absent variant-reversed-dark-ok "brd:PAL-08" "$FIX/mark-reversed.svg" --brief "$FIX/brief-roles-good.md"
run variant-no-brand-ink 0 "logo ink must be the brand role" "$FIX/no-ink.svg" --brief "$FIX/brief-roles-good.md"
absent variant-mono-exempt "brd:PAL-08" "$FIX/mark-mono-stray.svg" --brief "$FIX/brief-roles-good.md"
absent variant-no-roles "brd:PAL-08" "$FIX/stray-colour.svg" --brief "$FIX/brief-lowcontrast.md"

# CTR-06: the downloadable set
mkexp() { # mkexp <dir> <transparent true|false> [stem]: a complete export folder with real PNGs and a real zip
  python3 -I - "$1" "$2" "${3:-mark}" <<'PY'
import json, os, shutil, struct, sys, zipfile, zlib
d, t, stem = sys.argv[1], sys.argv[2] == "true", sys.argv[3]
shutil.rmtree(d, ignore_errors=True); os.makedirs(d + "/svg"); os.makedirs(d + "/png")
for f in os.listdir(os.path.dirname(os.path.abspath(d))):
    if f.endswith(".svg"): os.remove(os.path.join(os.path.dirname(os.path.abspath(d)), f))
sizes = [16, 32, 48, 64, 128, 256, 512, 1024]
def png(n):
    row = (b"\x00" + (b"\x10\x20\x30\xff" if not t else b"\x00\x00\x00\x00") * n)
    if t:  # a centred ink block, transparent elsewhere
        px = [(b"\x10\x20\x30\xff" if n // 4 <= x < 3 * n // 4 else b"\x00\x00\x00\x00") for x in range(n)]
        mid = b"\x00" + b"".join(px)
        rows = [mid if n // 4 <= y < 3 * n // 4 else b"\x00" + b"\x00\x00\x00\x00" * n for y in range(n)]
    else:
        rows = [row] * n
    def ch(k, b): return struct.pack(">I", len(b)) + k + b + struct.pack(">I", zlib.crc32(k + b))
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)) + ch(b"IDAT", zlib.compress(b"".join(rows))) + ch(b"IEND", b"")
open(d + "/svg/%s.svg" % stem, "w").write("<svg/>")
parent = os.path.dirname(os.path.abspath(d)); open(os.path.join(parent, stem + ".svg"), "w").write("<svg/>")
for s in sizes: open(d + "/png/%s-%d.png" % (stem, s), "wb").write(png(s))
json.dump({"sizes": sizes, "files": {stem: {}}}, open(d + "/manifest.json", "w"))
with zipfile.ZipFile(d + "/assets.zip", "w") as z:
    z.write(d + "/svg/%s.svg" % stem, "svg/%s.svg" % stem)
    for s in sizes: z.write(d + "/png/%s-%d.png" % (stem, s), "png/%s-%d.png" % (stem, s))
PY
}
mkdir -p proj; mkexp proj/exports true
run exports-complete 0 "" --exports proj/exports
absent exports-complete-clean "brd:CTR-06" --exports proj/exports
run exports-missing-folder 1 "no exports folder" --exports proj/nope
rm proj/exports/assets.zip
run exports-no-zip 1 "no zip bundle" --exports proj/exports
mkexp proj/exports true; rm proj/exports/png/mark-512.png
run exports-missing-png 1 "missing export file" --exports proj/exports
mkexp proj/exports false
run exports-opaque 1 "has a background" --exports proj/exports
# a renderer drops alpha for a fully opaque image: the reader must take RGB and still flag the background
mkexp proj/exports false
python3 -I - <<'PY'
import glob, struct, zlib
def chunks(b):
    p = 8
    while p < len(b):
        n, k = struct.unpack(">I4s", b[p:p+8]); yield k, b[p+8:p+8+n]; p += 12 + n
for f in glob.glob("proj/exports/png/mark-*.png"):
    b = open(f, "rb").read(); w = h = None; raw = b""
    for k, d in chunks(b):
        if k == b"IHDR": w, h = struct.unpack(">II", d[:8])
        if k == b"IDAT": raw += d
    raw = zlib.decompress(raw); st = w * 4 + 1
    rgb = b"".join(b"\x00" + b"".join(raw[y*st+1+4*x:y*st+4+4*x] for x in range(w)) for y in range(h))
    ch = lambda k, d: struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d))
    open(f, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(rgb)) + ch(b"IEND", b""))
PY
run exports-opaque-rgb 1 "has a background" --exports proj/exports
mkexp proj/exports false app-icon
absent exports-tile-exempt "has a background" --exports proj/exports
mkexp proj/exports true; echo '<svg/>' > proj/lockup-stacked.svg
run exports-not-listed 1 "not exported: lockup-stacked" --exports proj/exports
rm proj/lockup-stacked.svg
# the manifest is not trusted: a lying "transparent" flag, hostile names, junk shapes
mkexp proj/exports false; python3 -I -c "import json;p='proj/exports/manifest.json';m=json.load(open(p));m['files']['mark']={'transparent':True,'tile':True,'svg':'../../etc/passwd'};json.dump(m,open(p,'w'))"
run exports-lying-flag 1 "has a background" --exports proj/exports
mkexp proj/exports true; echo '{"files":{"../evil":{}}}' > proj/exports/manifest.json
run exports-hostile-stem 1 "unsafe file name" --exports proj/exports
echo '{"files":[1,2]}' > proj/exports/manifest.json
run exports-manifest-list 1 "manifest.json is malformed" --exports proj/exports
echo '[]' > proj/exports/manifest.json
run exports-manifest-array 1 "manifest.json is malformed" --exports proj/exports
mkexp proj/exports true; echo junk > proj/exports/png/mark-64.png
run exports-junk-png 1 "not a valid PNG" --exports proj/exports
mkexp proj/exports true; echo changed > proj/mark.svg
run exports-stale-copy 1 "differs from brand/mark.svg" --exports proj/exports
mkexp proj/exports true; echo notazip > proj/exports/assets.zip
run exports-bad-zip 1 "not a valid zip" --exports proj/exports
mkexp proj/exports true; python3 -I -c "import zipfile;zipfile.ZipFile('proj/exports/assets.zip','w').writestr('svg/mark.svg','x')"
run exports-thin-zip 1 "does not hold every exported file" --exports proj/exports

# brand sheet colours against the roles table, and rules_checked that tells the truth
mkdir -p sheetproj/brand && cp "$FIX/brief-roles-good.md" sheetproj/brand/brief.md && printf '| navy | #12324A |\n| tide | #1F6F8B |\n' > sheetproj/brand/brand-sheet.md
run sheet-stale-colour 0 "brand-sheet.md shows colours" --brief sheetproj/brand/brief.md
printf '| tide | #1F6F8B |\n| old | #F57C00 |\n' > sheetproj/brand/brand-sheet.md
absent sheet-category-colour-ok "brand-sheet.md shows colours" --brief sheetproj/brand/brief.md
run rules-checked-lists-brief-rules 0 "brief: EVD-02 POS-01 POS-02 POS-05 PAL-01" --brief "$FIX/brief-roles-good.md"
run rules-checked-lists-exports 1 "exports: CTR-06" --exports proj/nope

# JSON shape
python3 -I "$SCRIPT" "$FIX/live-text.svg" >/dev/null
python3 -I - <<'PY' && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL json shape"; }
import json
d = json.load(open("brand/checks/check.json"))
assert d["script"] == "brdcheck" and d["summary"]["fail_must"] >= 1
assert all({"id", "severity", "status", "file", "finding", "fix", "evidence"} <= set(f) for f in d["findings"])
PY


# hardening: brief variants made from the good brief
G="$FIX/brief-roles-good.md"
mkbrief() { sed "$2" "$G" > "$1"; }   # mkbrief <file> <sed expr>
mkbrief b-four-fam 's/^- type: .*/- type: Inter + Lora + Mono + Slab. Four roles./'
run typ05-fail 0 "fail brd:TYP-05" --brief b-four-fam
mkbrief b-three-fam 's/^- type: .*/- type: Inter + Lora + Mono. Three roles./'
run typ05-review 0 "extra one needs a stated role" --brief b-three-fam
mkbrief b-two-fam 's/^- type: .*/- type: Inter + Lora. Two roles./'
absent typ05-two-ok "brd:TYP-05" --brief b-two-fam
absent typ05-one-family "brd:TYP-05" --brief "$G"
mkbrief b-small 's/^- type: .*/- type: Inter. Smallest 9 px for captions./'
run typ06-small 0 "brd:TYP-06" --brief b-small
absent typ06-ok "brd:TYP-06" --brief "$G"
mkbrief b-tbd 's/^positioning: .*/positioning: TBD/'
run pos-placeholder 0 "brd:POS-01" --brief b-tbd
mkbrief b-short 's/^positioning: .*/positioning: a log viewer/'
run pos-too-short 0 "too short" --brief b-short
mkbrief b-dup 's/^| status | #B3261E .*/| brand | #B3261E | #FF8A80 | red 700\/300 |/'
run pal01-duplicate-role 0 "brd:PAL-01" --brief b-dup
mkbrief b-badhex 's/^| neutral | #5B6770/| neutral | #5B67/'
run pal01-invalid-hex 0 "brd:PAL-01" --brief b-badhex
mkbrief b-nobg '/^| background |/d'
run incomplete-not-run 0 "not run" --brief b-nobg

# POS-05: the story
python3 -I - "$G" <<'PY'
import re, sys
g = open(sys.argv[1]).read()
open("b-nostory.md", "w").write(re.sub(r"\n## Story.*", "\n", g, flags=re.S))
open("b-longstory.md", "w").write(g.rstrip("\n") + "\n\nThree.\n\nFour.\n\nFive.\n")
open("b-placeholder.md", "w").write(re.sub(r"\n## Story.*", "\n## Story\n\n<beat one>\n\n<!-- note -->\n", g, flags=re.S))
PY
run template-story-empty 0 "no '## Story' section" --brief "$HERE/../../../templates/brief.md"
run story-missing 0 "no '## Story' section" --brief b-nostory.md
run story-placeholder-ignored 0 "no '## Story' section" --brief b-placeholder.md
run story-too-long 0 "has 5 paragraphs" --brief b-longstory.md
mkbrief b-draft 's/^story-status: confirmed/story-status: assumed/'
run story-draft-review 0 "the story is a draft" --brief b-draft
mkbrief b-nostatus '/^story-status:/d'
run story-no-status-review 0 "story-status is 'not set'" --brief b-nostatus
absent story-confirmed-clean "brd:POS-05" --brief "$G"
run rules-checked-lists-pos05 0 "brief: EVD-02 POS-01 POS-02 POS-05" --brief "$G"

# hardening: SVG inputs and arguments
printf '<?xml version="1.0"?><?xml-stylesheet href="http://x/a.css"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8"><path d="M0 0h8v8z" fill="#000"/></svg>' > pi.svg
run pi-stylesheet 1 "brd:SEC-01" pi.svg
python3 -I -c "print('<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 8 8\">' + '<g>'*3000 + '</g>'*3000 + '</svg>')" > deep.svg
run deep-nesting 1 "brd:CTR-01" deep.svg
mkdir -p brand
run out-is-folder 2 "must be a file path" --out brand "$FIX/stray-colour.svg"
mkdir -p walk/exports walk/concepts walk/icons && cp "$FIX/stray-colour.svg" walk/exports/a.svg && cp "$FIX/stray-colour.svg" walk/concepts/b.svg && cp "$FIX/stray-colour.svg" walk/icons/c.svg
run walk-skips-copies 2 "nothing to check" walk
cp "$FIX/role-colour.svg" walk/UPPER.SVG
run walk-case-insensitive 0 "1 files" walk

# masks and clip paths are mattes, not painted colour (PAL-08, CAP-01)
absent mask-not-palette "brd:PAL-08" "$FIX/mask-master.svg" --brief "$FIX/brief-roles-good.md"
absent mask-not-counted "brd:CAP-01" "$FIX/mask-master.svg"
python3 -I "$SCRIPT" "$FIX/mask-master.svg" --brief "$FIX/brief-roles-good.md" >/dev/null
python3 -I -c "import json,sys;sys.exit(0 if json.load(open('brand/checks/check.json'))['files']==['$FIX/mask-master.svg'] else 1)" && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL mask json"; }
# a real stray colour outside the mask is still caught
run mask-stray-outside 0 "brd:PAL-08" "$FIX/stray-colour.svg" --brief "$FIX/brief-roles-good.md"

# CRF-03: endpoints rounded to 2 decimals sit about 0.01 degrees off an exact angle and count as exact
absent rounded-60-exact "brd:CRF-03" "$FIX/rot60.svg"
run near-angle-still-flagged 0 "brd:CRF-03" "$FIX/near-angle.svg"

# --root: brand/ resolves against it, a non-directory exits 2
mkdir -p rootproj/brand && cp "$FIX/brief-roles-good.md" rootproj/brand/brief.md
run root-ok 0 "" --root rootproj --brief brand/brief.md
[ -s rootproj/brand/checks/check.json ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL --root should write rootproj/brand/checks/check.json"; }
run root-not-dir 2 "not a directory" --root "$FIX/good.svg" --brief x
run root-missing 2 "not a directory" --root "$WORK/nope" --brief x

# --stage: brief-level rules need kit sections; at concept stage they print n/a
run stage-auto-concept 0 "n/a brd:POS-05" --brief "$FIX/brief-roles-concept.md"
run stage-auto-concept-pos02 0 "n/a brd:POS-02" --brief "$FIX/brief-roles-concept.md"
absent stage-auto-concept-no-fail "^fail" --brief "$FIX/brief-roles-concept.md"
run stage-auto-concept-typ01 0 "n/a brd:TYP-01" "$FIX/wordmark-glyph.svg" --brief "$FIX/brief-roles-concept.md"
run stage-kit-fails 0 "fail brd:POS-05" --stage kit --brief "$FIX/brief-roles-concept.md"
run stage-kit-pos02 0 "fail brd:POS-02" --stage kit --brief "$FIX/brief-roles-concept.md"
run stage-kit-typ01 1 "fail brd:TYP-01" --stage kit "$FIX/wordmark-glyph.svg" --brief "$FIX/brief-roles-concept.md"
run stage-concept-forced 0 "n/a brd:POS-05" --stage concept --brief "$FIX/brief-roles-bad.md"
run stage-auto-kit 0 "" --brief "$FIX/brief-roles-bad.md"
run stage-auto-kit-fails 0 "fail brd:POS-02" --brief "$FIX/brief-roles-bad.md"

# EVD-03: a declared pair-cue closes the review; EVD-04 is untouched
run pair-review-without-cue 0 "review brd:EVD-03" --brief "$FIX/brief-roles-pair.md"
run pair-cue-pass 0 "pass brd:EVD-03.*each status chip carries a text label" --brief "$FIX/brief-roles-pair-cue.md"
absent pair-cue-no-review "review brd:EVD-03" --brief "$FIX/brief-roles-pair-cue.md"
sed 's/^pair-cue: .*/pair-cue: TBD/' "$FIX/brief-roles-pair-cue.md" > pair-ph.md
run pair-cue-placeholder-ignored 0 "review brd:EVD-03" --brief pair-ph.md
python3 -I "$SCRIPT" --brief "$FIX/brief-roles-pair.md" >/dev/null; a=$(python3 -I -c "import json;print(sorted((f['id'],f['status']) for f in json.load(open('brand/checks/check.json'))['findings'] if f['id']=='brd:EVD-04'))")
python3 -I "$SCRIPT" --brief "$FIX/brief-roles-pair-cue.md" >/dev/null; b=$(python3 -I -c "import json;print(sorted((f['id'],f['status']) for f in json.load(open('brand/checks/check.json'))['findings'] if f['id']=='brd:EVD-04'))")
[ "$a" = "$b" ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL pair-cue must not change EVD-04"; }

echo "brdcheck tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
