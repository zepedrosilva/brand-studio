#!/bin/sh
# Checks the Claude Code guidance files of this repo. Prints one "ID: message (severity)" line per finding.
# Exit 1 when any must rule fails; should and may findings do not fail.
# Usage: sh scripts/check-repo-docs.sh [repo-dir]
# Optional: REPO_DOCS_DENYLIST=<file kept outside the repo> with one pattern per line (SEC-01).
# Hook checks (HOK) need python3 to read settings.json; without it they are skipped with a note.
set -u

# Thresholds, in one place. The hook helper .claude/hooks/lessons.py uses the same numbers.
WARN_CLAUDE_LINES=150   # assumption: early warning
MAX_CLAUDE_LINES=200    # vendor guidance: keep CLAUDE.md under 200 lines
MAX_IMPORT_HOPS=4       # vendor: @path imports nest at most four hops
MAX_LESSONS=15          # assumption
STALE_DAYS=90           # assumption
MAX_EVIDENCE_CHARS=80   # assumption: a pointer is short
MAX_ADR_LINES=80        # assumption: about two pages
MAX_HOOKS=3             # assumption
LESSON_RE='^- [0-9]{4}-[0-9]{2}-[0-9]{2} · .+ · .+ · promote-to: (CLAUDE\.md|rule|adr|check|skill|none)$'
ADR_STATUS_RE='^(proposed|accepted|rejected|deprecated|superseded by .+)$'

cd "${1:-.}" || exit 2
LC_ALL=C; export LC_ALL
tmp=$(mktemp -d) || exit 2
trap 'rm -rf "$tmp"' EXIT

nm=0; ns=0; nmay=0
must()   { echo "$1: $2 (must)"; nm=$((nm + 1)); }
should() { echo "$1: $2 (should)"; ns=$((ns + 1)); }
may()    { echo "$1: $2 (may)"; nmay=$((nmay + 1)); }

# Print a file without carriage returns, fenced code blocks and HTML comments.
strip() {
  awk '
    { sub(/\r$/, "") }
    /^```/ { f = !f; next }
    f { next }
    { line = $0
      while (1) {
        if (c) { i = index(line, "-->"); if (!i) { line = ""; break } line = substr(line, i + 3); c = 0 }
        i = index(line, "<!--"); if (!i) break
        pre = substr(line, 1, i - 1); rest = substr(line, i + 4)
        j = index(rest, "-->")
        if (j) line = pre substr(rest, j + 3); else { line = pre; c = 1; break }
      }
      print line }' "$1"
}

# Decode percent escapes in a link path (%20 to a space).
pdecode() {
  printf '%s\n' "$1" | awk '{
    s = $0; o = ""; h = "0123456789abcdef"
    while ((i = index(s, "%")) > 0) {
      x = tolower(substr(s, i + 1, 2)); a = index(h, substr(x, 1, 1)) - 1; b = index(h, substr(x, 2, 1)) - 1
      if (length(x) == 2 && a >= 0 && b >= 0) { o = o substr(s, 1, i - 1) sprintf("%c", a * 16 + b); s = substr(s, i + 3) }
      else { o = o substr(s, 1, i); s = substr(s, i + 1) }
    }
    print o s }'
}

# LOC-01: fixed locations
for p in CLAUDE.md docs/README.md docs/context.md docs/decisions docs/lessons.md docs/open-questions.md .claude/settings.json; do
  [ -e "$p" ] || must LOC-01 "$p is missing: create it"
done

# LOC-06: what must be committed is not ignored by git (skipped outside a git repo or without git)
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  for p in CLAUDE.md .claude/settings.json .claude/hooks .claude/rules .claude/skills docs; do
    [ -e "$p" ] || continue
    if git check-ignore -q -- "$p" 2>/dev/null; then
      rule=$(git check-ignore -v -- "$p" 2>/dev/null | cut -f1)
      must LOC-06 "$p is ignored by git ($rule): narrow that rule so it is committed; ignore only .claude/settings.local.json and CLAUDE.local.md"
    fi
  done
fi

# LOC-02: CLAUDE.md size
if [ -f CLAUDE.md ]; then
  n=$(wc -l < CLAUDE.md); n=$((n + 0))
  if [ "$n" -ge "$MAX_CLAUDE_LINES" ]; then
    should LOC-02 "CLAUDE.md is $n lines, cap $MAX_CLAUDE_LINES: move detail to .claude/rules/, a skill or docs/"
  elif [ "$n" -ge "$WARN_CLAUDE_LINES" ]; then
    should LOC-02 "CLAUDE.md is $n lines, warn from $WARN_CLAUDE_LINES: run the tidy-docs skill"
  fi
fi

# LOC-03: relative links resolve
{ [ -f CLAUDE.md ] && echo CLAUDE.md; find docs/ .claude/rules/ -name '*.md' 2>/dev/null | sed 's#//#/#' | sort; } > "$tmp/md"
while IFS= read -r f; do
  dir=$(dirname "$f")
  # shellcheck disable=SC2016 # backticks are literal: inline code spans are skipped
  strip "$f" | sed 's/`[^`]*`//g' > "$tmp/body"
  # inline links [text](path) and reference definitions [ref]: path
  { grep -oE '\]\([^)[:space:]]+\)' "$tmp/body" | sed -e 's/^](//' -e 's/)$//'
    grep -E '^[[:space:]]{0,3}\[[^]]+\]:[[:space:]]*<?[^[:space:]>]+' "$tmp/body" \
      | sed -E 's/^[[:space:]]*\[[^]]+\]:[[:space:]]*<?([^[:space:]>]+).*/\1/'
  } > "$tmp/links"
  while IFS= read -r t; do
    t=${t%%#*}
    case "$t" in *%*) t=$(pdecode "$t") ;; esac
    case "$t" in ""|http://*|https://*|mailto:*) continue ;; /*) p=".$t" ;; *) p="$dir/$t" ;; esac
    [ -e "$p" ] || must LOC-03 "$f links to $t, which does not exist: fix or remove the link"
  done < "$tmp/links"
done < "$tmp/md"

# LOC-03: @path imports resolve, nest at most MAX_IMPORT_HOPS hops, and do not loop
imports() {
  idir=$(dirname "$1")
  # shellcheck disable=SC2016
  strip "$1" | sed 's/`[^`]*`//g' | grep -oE '(^|[[:space:]])@[^[:space:]]+' \
    | sed -e 's/^[[:space:]]*@//' -e 's/[.,;:)]*$//' | grep -E '[./]' | while IFS= read -r i; do
      # shellcheck disable=SC2088
      # shellcheck disable=SC2088 # a literal "~/" prefix marks a personal import, which is skipped
      case "$i" in "~/"*) ;; /*) echo "$i" ;; *) if [ "$idir" = . ]; then echo "$i"; else echo "$idir/$i"; fi ;; esac
    done
}
if [ -f CLAUDE.md ]; then
  echo CLAUDE.md > "$tmp/level"; cp "$tmp/level" "$tmp/seen"; hop=0
  while [ -s "$tmp/level" ]; do
    hop=$((hop + 1)); : > "$tmp/next"
    while IFS= read -r f; do
      imports "$f" > "$tmp/imp"
      while IFS= read -r i; do
        if [ -f "$i" ]; then echo "$i" >> "$tmp/next"
        else must LOC-03 "$f imports @$i, which does not exist: fix the path"; fi
      done < "$tmp/imp"
    done < "$tmp/level"
    if [ "$hop" -gt "$MAX_IMPORT_HOPS" ] && [ -s "$tmp/next" ]; then
      # shortcut: a file seen earlier in the walk means a loop; paths are compared as written, not normalised.
      if grep -qxF -f "$tmp/next" "$tmp/seen"; then
        must LOC-03 "import cycle: @path imports from CLAUDE.md loop back to a file already imported: remove one import"
      else
        must LOC-03 "@path imports from CLAUDE.md nest more than $MAX_IMPORT_HOPS hops: flatten them"
      fi
      break
    fi
    cat "$tmp/next" >> "$tmp/seen"
    mv "$tmp/next" "$tmp/level"
  done
fi

# LOC-04: path rules have valid paths frontmatter. Output of the awk: "<MUST|MAY> <message>".
find .claude/rules/ -name '*.md' 2>/dev/null | sed 's#//#/#' | sort > "$tmp/rules"
while IFS= read -r f; do
  msg=$(awk '
    function check(v, n,  c) {
      gsub(/^[ ]+|[ ]+$/, "", v)
      if (v == "") return
      items++
      c = substr(v, 1, 1)
      if (c == "\"" || c == "\047") return
      if (index("*{[&!%@|>`", c) || v ~ /: / || v ~ / #/)
        if (bad == "") bad = "unquoted value " v " at line " n " is not valid YAML: quote it"
    }
    { sub(/\r$/, "") }
    NR == 1 { if ($0 != "---") exit; fm = 1; next }
    $0 == "---" { closed = 1; exit }
    {
      if ($0 ~ /\t/) { if (bad == "") bad = "tab at line " NR; next }
      if ($0 ~ /^paths:/) {
        has = 1; inp = 1; v = $0; sub(/^paths:[ ]*/, "", v)
        if (v == "") next
        inp = 0
        if (v ~ /^\[[ ]*\]$/) next
        if (v ~ /^\[.*\]$/) { k = split(substr(v, 2, length(v) - 2), parts, ","); for (j = 1; j <= k; j++) check(parts[j], NR) }
        else check(v, NR)
        next
      }
      if (inp && $0 ~ /^[ ]*-([ ]|$)/) { v = $0; sub(/^[ ]*-/, "", v); check(v, NR); next }
      if ($0 ~ /^[ ]*-([ ]|$)/) next
      if ($0 ~ /^[A-Za-z_][A-Za-z0-9_-]*:/) { inp = 0; next }
      if ($0 ~ /^[ ]*(#.*)?$/) next
      if (bad == "") bad = "not YAML at line " NR
    }
    END {
      if (!fm) exit
      if (!closed) print "MUST frontmatter is not closed"
      else if (bad != "") print "MUST " bad
      else if (!has) print "MAY no paths key, so the rule loads in every session"
      else if (!items) print "MUST paths has no entries"
    }' "$f")
  case "$msg" in
    MUST*) must LOC-04 "$f: ${msg#MUST }: fix the frontmatter (a rule whose frontmatter does not parse loads for every file)" ;;
    MAY*) may LOC-04 "$f: ${msg#MAY }: add paths if it only matters for part of the tree" ;;
  esac
done < "$tmp/rules"

# LSN-01, LSN-02, LSN-03, LSN-05: lessons
if [ -f docs/lessons.md ]; then
  strip docs/lessons.md | grep -E '^[-*+] ' > "$tmp/lessons"
  grep -nvE "$LESSON_RE" "$tmp/lessons" | cut -d: -f1 > "$tmp/bad"
  while IFS= read -r k; do
    line=$(sed -n "${k}p" "$tmp/lessons")
    fixed=$(printf '%s\n' "$line" | sed -E 's/ · promote-to: (test|lint)$/ · promote-to: check/')
    if [ "$fixed" != "$line" ] && printf '%s\n' "$fixed" | grep -qE "$LESSON_RE"; then
      old=${line##*promote-to: }
      must LSN-01 "docs/lessons.md lesson $k uses the old value 'promote-to: $old': replace it with 'promote-to: check'"
      continue
    fi
    must LSN-01 "docs/lessons.md lesson $k does not match '- YYYY-MM-DD · <evidence> · <rule> · promote-to: <CLAUDE.md|rule|adr|check|skill|none>': rewrite it"
  done < "$tmp/bad"
  today=${CHECK_TODAY:-$(date +%Y-%m-%d)}
  awk -F ' · ' -v max="$MAX_EVIDENCE_CHARS" -v stale="$STALE_DAYS" -v today="$today" '
    function days(s,  y, m, d) {
      y = substr(s, 1, 4) + 0; m = substr(s, 6, 2) + 0; d = substr(s, 9, 2) + 0
      if (m < 3) { y--; m += 12 }
      return int(365.25 * y) + int(30.6001 * (m + 1)) + d
    }
    $1 ~ /^- [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ {
      y = substr($1, 3, 4) + 0; m = substr($1, 8, 2) + 0; d = substr($1, 11, 2) + 0
      split("31 28 31 30 31 30 31 31 30 31 30 31", dim, " ")
      if (m == 2 && (y % 4 == 0 && (y % 100 != 0 || y % 400 == 0))) dim[2] = 29
      if (m < 1 || m > 12 || d < 1 || d > dim[m]) { print "LSN-01 lesson " NR ": date " substr($1, 3) " does not exist: fix it"; next }
    }
    NF >= 4 && $1 ~ /^- [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]$/ {
      e = $2
      if (e ~ /"|“|”/ || e ~ /^>/) print "LSN-02 lesson " NR ": evidence looks like quoted text: use a pointer (PR, issue, commit, ADR, file)"
      else if (length(e) > max) print "LSN-02 lesson " NR ": evidence is over " max " characters: use a pointer"
      if (match($0, /https?:\/\/[^\/ )]+/)) {
        h = substr($0, RSTART, RLENGTH); sub(/^https?:\/\//, "", h); sub(/:.*/, "", h)
        if (h !~ /\./ || h ~ /\.(local|internal|corp|lan|intranet)$/ || h ~ /^(10|127)\./ || h ~ /^192\.168\./ || h ~ /^172\.(1[6-9]|2[0-9]|3[01])\./)
          print "LSN-02 lesson " NR ": links to an internal host: remove the URL"
      }
      if (days(today) - days(substr($1, 3)) > stale) print "LSN-05 lesson " NR ": older than " stale " days: review, promote or delete it"
    }' "$tmp/lessons" > "$tmp/lsn"
  while IFS= read -r l; do
    id=${l%% *}
    case "$id" in LSN-01|LSN-02) must "$id" "docs/lessons.md ${l#* }" ;; *) may "$id" "docs/lessons.md ${l#* }" ;; esac
  done < "$tmp/lsn"
  n=$(wc -l < "$tmp/lessons"); n=$((n + 0))
  if [ "$n" -gt "$MAX_LESSONS" ]; then
    should LSN-03 "docs/lessons.md has $n lessons, cap $MAX_LESSONS: promote or prune with the tidy-docs skill"
  fi
fi

# ADR-01 to ADR-04: decision records. Status comes from a "status:" line (MADR front matter,
# "Status: x") or from a "## Status" section (Nygard, adr-tools).
if [ -d docs/decisions ]; then
  find docs/decisions/ -maxdepth 1 -type f -name '*.md' ! -name README.md 2>/dev/null | sed 's#.*/##' | sort > "$tmp/adrs"
  while IFS= read -r a; do
    if ! echo "$a" | grep -qE '^[0-9]{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$'; then
      must ADR-01 "docs/decisions/$a: name it NNNN-title-with-dashes.md"; continue
    fi
    [ "$a" = 0000-template.md ] && continue
    f=docs/decisions/$a
    grep -qE '^# ' "$f" || must ADR-02 "$f has no title line: add '# <title>'"
    for s in context decision consequences; do
      grep -qiE "^#{2,3} .*$s" "$f" || must ADR-02 "$f has no $s section: add it"
    done
    st=$(awk '
      { sub(/\r$/, ""); l = tolower($0) }
      l ~ /^status:/ { sub(/^[^:]*:[ \t]*/, ""); print; exit }
      want && NF { print; exit }
      l ~ /^#+[ ]*status[ ]*$/ { want = 1 }' "$f" | sed 's/[[:space:]]*$//' | tr -d '"' | tr '[:upper:]' '[:lower:]')
    if [ -z "$st" ]; then
      must ADR-02 "$f has no status: add 'status: proposed' or a '## Status' section"
    elif ! echo "$st" | grep -qE "$ADR_STATUS_RE"; then
      must ADR-02 "$f status '$st' is not proposed, accepted, rejected, deprecated or superseded by NNNN"
    fi
    case "$st" in superseded*)
      echo "$st" | grep -qE '[0-9]{4}' || must ADR-03 "$f is superseded but does not name its successor: write 'superseded by NNNN'" ;;
    esac
    n=$(wc -l < "$f"); n=$((n + 0))
    if [ "$n" -gt "$MAX_ADR_LINES" ]; then
      should ADR-04 "$f is $n lines, cap $MAX_ADR_LINES: keep the context, decision and consequences"
    fi
  done < "$tmp/adrs"
  sed -n 's/^\([0-9][0-9][0-9][0-9]\)-.*/\1/p' "$tmp/adrs" | sort | uniq -d > "$tmp/dups"
  while IFS= read -r k; do must ADR-01 "number $k is used by more than one record in docs/decisions: renumber the newer one"; done < "$tmp/dups"
fi

# HOK-01, HOK-02, HOK-05: commands under the "hooks" key of settings.json only (not statusLine or others)
if [ -f .claude/settings.json ]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 -I - .claude/settings.json > "$tmp/cmds" 2>/dev/null <<'EOF'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    for groups in data.get("hooks", {}).values():
        for g in groups:
            for h in g.get("hooks", []):
                if h.get("type", "command") == "command" and isinstance(h.get("command"), str):
                    print(h["command"].replace("\n", " "))
except Exception:
    print("\tINVALID")
EOF
    if grep -q "$(printf '\t')INVALID" "$tmp/cmds"; then
      must HOK-01 ".claude/settings.json is not valid JSON or its hooks have an unexpected shape: no hook will run; fix the file"
      : > "$tmp/cmds"
    fi
  else
    may HOK-01 "python3 not found: hook checks skipped"
    : > "$tmp/cmds"
  fi
  : > "$tmp/keys"
  while IFS= read -r c; do
    case "$c" in
      *'"${CLAUDE_PROJECT_DIR}/'*) ;;
      *)
        echo "$c" >> "$tmp/keys"
        if printf '%s\n' "$c" | grep -qE '\.(sh|py|js|mjs|cjs|ts|rb|pl)([^A-Za-z0-9]|$)'; then
          must HOK-02 "hook command does not use a quoted \"\${CLAUDE_PROJECT_DIR}/...\" path: $c"
        fi
        continue ;;
    esac
    p=$(printf '%s\n' "$c" | sed 's/.*"\${CLAUDE_PROJECT_DIR}\/\([^"]*\)".*/\1/')
    echo "$p" >> "$tmp/keys"
    if [ ! -f "$p" ]; then
      must HOK-01 "hook script $p does not exist: restore it or remove the hook"
    else
      case "$c" in '"${CLAUDE_PROJECT_DIR}'*) [ -x "$p" ] || must HOK-01 "hook script $p is not executable: chmod +x it" ;; esac
    fi
  done < "$tmp/cmds"
  n=$(wc -l < "$tmp/keys"); n=$((n + 0))
  if [ "$n" -gt "$MAX_HOOKS" ]; then
    should HOK-05 ".claude/settings.json registers $n hook commands, cap $MAX_HOOKS: keep only rules with zero exceptions"
  fi
  sort "$tmp/keys" | uniq -d > "$tmp/dupkeys"
  while IFS= read -r k; do should HOK-05 "hook registered more than once: $k"; done < "$tmp/dupkeys"
fi

# SEC-01: secrets, internal hosts and organisation names. Matched content is never printed.
# Built-in secret patterns run always; REPO_DOCS_DENYLIST adds your own. A line holding
# "repo-docs-allow: SEC-01" waives a built-in hit (for example an example key in a doc).
for p in CLAUDE.md docs .claude scripts; do [ -e "$p" ] && echo "$p"; done > "$tmp/scan"
if [ -s "$tmp/scan" ]; then
  cat > "$tmp/secrets" <<'EOF'
-----BEGIN [A-Z ]*PRIVATE KEY-----
AKIA[0-9A-Z]{16}
gh[pousr]_[A-Za-z0-9]{30,}
[A-Za-z0-9-]+\.internal([^A-Za-z0-9-]|$)
EOF
  # shellcheck disable=SC2046 # paths are fixed names without spaces
  grep -rHnIiE -f "$tmp/secrets" --exclude=settings.local.json --exclude=check-repo-docs.sh $(cat "$tmp/scan") \
    | grep -v 'repo-docs-allow: SEC-01' | cut -d: -f1,2 > "$tmp/hits"
  # api_key or secret assignments: only a literal value counts, quoted (16 or more characters, no
  # spaces) or a bare token of 16 or more characters with letters and digits (assumption).
  # shellcheck disable=SC2046
  grep -rHnIiE '(api[_-]?key|secret)["'\'']?[[:space:]]*[:=]' --exclude=settings.local.json --exclude=check-repo-docs.sh $(cat "$tmp/scan") \
    | grep -v 'repo-docs-allow: SEC-01' | awk '{
      p = index($0, ":"); f = substr($0, 1, p - 1); r = substr($0, p + 1)
      q = index(r, ":"); n = substr(r, 1, q - 1); s = substr(r, q + 1)
      if (!match(tolower(s), /(api[_-]?key|secret)["\047]?[ \t]*[:=][ \t]*/)) next
      v = substr(s, RSTART + RLENGTH); c = substr(v, 1, 1)
      if (c == "\"" || c == "\047") {
        v = substr(v, 2); e = index(v, c); if (!e) next
        v = substr(v, 1, e - 1); ok = (v !~ /[ \t]/)
      } else {
        if (!match(v, /^[A-Za-z0-9+\/=_.-]+/)) next
        rest = substr(v, RLENGTH + 1); v = substr(v, 1, RLENGTH)
        ok = (v ~ /[0-9]/ && v ~ /[A-Za-z]/ && rest !~ /^\(/)
      }
      if (ok && length(v) >= 16) print f ":" n
    }' >> "$tmp/hits"
  sort -u "$tmp/hits" -o "$tmp/hits"
  while IFS= read -r h; do must SEC-01 "$h looks like a secret or an internal host (content not shown): remove it and rotate it if real, or add 'repo-docs-allow: SEC-01' to the line if it is a harmless example"; done < "$tmp/hits"
  if [ -n "${REPO_DOCS_DENYLIST:-}" ] && [ -f "$REPO_DOCS_DENYLIST" ]; then
    grep -vE '^[[:space:]]*(#|$)' "$REPO_DOCS_DENYLIST" > "$tmp/deny"
    if [ -s "$tmp/deny" ]; then
      # shellcheck disable=SC2046
      grep -rHnIiE -f "$tmp/deny" --exclude=settings.local.json $(cat "$tmp/scan") > "$tmp/dhits" 2>/dev/null
      if [ $? -eq 2 ]; then must SEC-01 "the deny list in REPO_DOCS_DENYLIST has an invalid pattern: fix it"; fi
      cut -d: -f1,2 "$tmp/dhits" > "$tmp/hits"
      while IFS= read -r h; do must SEC-01 "$h matches the local deny list (content not shown): remove it"; done < "$tmp/hits"
    fi
  fi
fi

echo "Summary: $nm must, $ns should, $nmay may."
[ "$nm" -eq 0 ] || exit 1
exit 0
