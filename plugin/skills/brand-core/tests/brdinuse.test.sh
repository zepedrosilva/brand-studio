#!/usr/bin/env bash
# Regression test for scripts/brdinuse.py. Run: bash tests/brdinuse.test.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/brdinuse.py"
FIX="$HERE/fixtures"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK" || exit 1
pass=0; fail=0

# run <name> <expected exit> <expected text or empty> <args...>
run() {
  local name="$1" code="$2" want="$3"; shift 3
  out="$(python3 -I "$SCRIPT" "$@" 2>&1)"; rc=$?
  ok=1
  [ "$rc" -eq "$code" ] || ok=0
  if [ -n "$want" ]; then echo "$out" | grep -q -- "$want" || ok=0; fi
  if [ "$ok" -eq 1 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $name (exit $rc, want $code, text '$want')"; echo "$out" | head -5; fi
}
# check <name> <file> <grep -c count wanted> <pattern>: count of matching lines in a file
count() {
  local name="$1" f="$2" want="$3" pat="$4" n
  n="$(grep -c -- "$pat" "$f")"
  if [ "$n" -eq "$want" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $name: '$pat' matched $n lines in $f, want $want"; fi
}

mkdir -p proj/brand
cp "$FIX/brief-roles-good.md" proj/brand/brief.md
cp "$FIX/role-colour.svg" proj/brand/mark.svg
cd proj || exit 1

run basic 0 "pairs clear their floor" 
count basic-file-written brand/applications.html 1 "<title>Brand applications</title>"
count no-external-links brand/applications.html 0 "https\?://"
count one-inline-script brand/applications.html 1 "<script>if(/\[?&\]embed"
count no-external-script brand/applications.html 0 "<script[^>]*src"
run no-exports-note 0 "no exports folder"
run no-reversed-note 0 "no mark-reversed.svg"

# failing pair: a pale neutral
sed 's/^| neutral | #5B6770/| neutral | #AAB4BB/' brand/brief.md > low.md
run low-contrast 0 "fail brd:PAL-09" --brief low.md --out brand/low.html
count low-contrast-flagged brand/low.html 1 "below floor"

# input errors exit 2
sed '/^| background |/d' brand/brief.md > nobg.md
run missing-role 2 "lacks a valid" --brief nobg.md
run missing-brief 2 "cannot read brief" --brief nope.md
run out-outside 2 "inside the brand folder" --out ../evil.html
run out-is-folder 2 "inside the brand folder" --out brand
run out-not-html 2 "inside the brand folder" --out brand/x.txt
mkdir -p empty/brand && cp brand/brief.md empty/brand/
( cd empty && run no-mark 2 "draw the mark first" )

# hostile text and files cannot add script to the page
{ printf 'name: <script>alert(1)</script>\nconcept: <img src=x onerror=alert(1)>\n'; cat brand/brief.md; } > evil.md
printf '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8"><script>alert(1)</script><rect width="8" height="8" fill="#12324A"/></svg>' > brand/mark-reversed.svg
run hostile 0 "pairs clear" --brief evil.md --out brand/evil.html
count hostile-no-script brand/evil.html 0 "<script>alert"
count hostile-no-onerror brand/evil.html 0 "<img src=x"
count hostile-name-escaped brand/evil.html 1 "&lt;script&gt;alert(1)&lt;/script&gt; applications</title>"
rm brand/mark-reversed.svg

# real exports are used when they exist
mkdir -p brand/exports/png
python3 -I - <<'PY'
import struct, zlib
def ch(k, d): return struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d))
for stem, n in (("mark", 16), ("mark", 32)):
    raw = b"".join(b"\x00" + b"\x12\x32\x4a\xff" * n for _ in range(n))
    open("brand/exports/png/%s-%d.png" % (stem, n), "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 6, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b""))
PY
run with-exports 0 "pairs clear"
count with-exports-no-note brand/applications.html 0 "no exports folder"
count with-exports-zoom brand/applications.html 1 "16 px, shown 6"

# the story at the top
count story-shown brand/applications.html 1 "Tideline is a timeline view for backend engineers"
count story-confirmed-no-draft brand/applications.html 0 "Draft story"
sed 's/^story-status: confirmed/story-status: assumed/' brand/brief.md > draft.md
run story-draft 0 "pairs clear" --brief draft.md --out brand/draft.html
count story-draft-marked brand/draft.html 1 "Draft story, not yet confirmed"
python3 -I - <<'PY'
import re
g = open("brand/brief.md").read()
open("nostory.md", "w").write("audience: Backend engineers\nconcept: A timeline view for logs.\ntone: calm, exact\n" + re.sub(r"\n## Story.*", "\n", g, flags=re.S))
open("evilstory.md", "w").write(g.rstrip("\n") + "\n\n<script>alert(1)</script> and <img src=x onerror=alert(1)>\n")
open("longstory.md", "w").write(g.rstrip("\n") + "\n\nThree.\n\nFour.\n\nFive.\n")
PY
run story-fallback 0 "pairs clear" --brief nostory.md --out brand/fallback.html
count fallback-facts brand/fallback.html 1 'class="facts"'
count fallback-audience brand/fallback.html 1 "Backend engineers"
count fallback-no-story brand/fallback.html 0 'class="story"'
run story-escaped 0 "pairs clear" --brief evilstory.md --out brand/evilstory.html
count story-no-script brand/evilstory.html 0 "<script>alert"
count story-no-onerror brand/evilstory.html 0 "<img src=x"
run story-capped 0 "showing the first 4" --brief longstory.md --out brand/long.html

# neutral chrome, light only
count page-white brand/applications.html 1 '--bg:#FFFFFF;--surface:#FFFFFF;--ink:#1A1A1A;--muted:#5F6368;--line:#E5E7EB'
count no-dark-blocks brand/applications.html 0 "prefers-color-scheme\|data-theme"
count no-brand-bg-var brand/applications.html 0 '--bg:#F6F8F9'
# slide footer in flow, stacked tables, embed
count slide-footer-flow brand/applications.html 1 "margin-top:auto"
count table-labels brand/applications.html 1 'content:attr(data-label)'
count cell-labels brand/applications.html 1 'data-label="Measured">'
count embed-css brand/applications.html 1 '\.embed \.intro{display:none}'
# phone app first, count word computed
count six-places brand/applications.html 1 'The kit placed in six everyday applications'
first="$(grep -o '<h2>[^<]*</h2>' brand/applications.html | head -1)"
if [ "$first" = "<h2>Phone app</h2>" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL phone-first: $first"; fi
# each status row has its own label and shape
printf '| status | #B3261E | #FF8A80 | red 700/300 |\n| status | #8A5A00 | #FFC857 | amber 700/300 |\n' > st.txt
sed '/^| status |/d' brand/brief.md | sed '/^| text |/r st.txt' > two.md
run two-status 0 "pairs clear" --brief two.md --out brand/two.html
count status-red brand/two.html 1 'Needs attention (red)</span>'
count status-amber brand/two.html 1 'Needs attention (amber)</span>'
count status-dash brand/two.html 1 'M3.5 8h9'
count app-chip-pair brand/two.html 1 'Chip text (Needs attention (amber))'
sed 's/amber 700/green 700/' two.md > ok.md
run tick-status 0 "pairs clear" --brief ok.md --out brand/ok.html
count status-passed brand/ok.html 1 'Passed (green)</span>'
run one-status 0 "pairs clear" --brief brand/brief.md --out brand/one.html
count one-status-brand-chip brand/one.html 1 '>Active</b>'
# --root
( cd .. && run root 0 "wrote" --root proj )
run root-bad 2 "not a directory" --root nope

echo "brdinuse tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
