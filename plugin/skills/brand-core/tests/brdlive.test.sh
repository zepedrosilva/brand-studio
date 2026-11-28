#!/usr/bin/env bash
# Regression test for scripts/brdlive.py. Run: bash tests/brdlive.test.sh
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../scripts/brdlive.py"
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
# has <name> <file> <fixed text>: the file contains the text
has() {
  if grep -qF -- "$3" "$2"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $1: '$3' not in $2"; fi
}
lacks() {
  if grep -qF -- "$3" "$2"; then fail=$((fail+1)); echo "FAIL $1: '$3' found in $2"; else pass=$((pass+1)); fi
}

mkdir -p proj/brand
cp "$FIX/brief-roles-good.md" proj/brand/brief.md
cp "$FIX/role-colour.svg" proj/brand/mark.svg
cd proj || exit 1

# the page and the state
run refresh 0 "refresh ok" refresh
has page-exists brand/index.html "Brand design brief"
lacks placeholder-replaced brand/index.html "/*__STATE__*/null"
has state-written brand/live/state.json '"steps"'
run step 0 "step ok" step brief "done" --note "assumed two fields"
has step-recorded brand/live/state.json "assumed two fields"
run step-bad-id 2 "unknown step" step nope "done"
run step-bad-status 2 "" step brief weird

# questions and answers
run ask 0 "ask ok" ask q1 --text "Which name?" --suggest "Pantry Clock"
has question-open brand/live/state.json '"status": "open"'
run ask-twice 2 "already exists" ask q1 --text x --suggest y
run wait-timeout 3 "no answer" wait q1 --timeout 1
run answer 0 "answered" answer q1 "Pantry Clock"
run wait-answer 0 '"answer": "Pantry Clock"' wait q1 --timeout 5
run answer-twice 2 "already answered" answer q1 other
run answer-unknown 2 "no question" answer zzz x

# the concept pick
run ask-pick 0 "ask ok" ask pick --kind pick --text "Which concept?" --suggest a --option a --option b --option c
run pick-bad 2 "must be one of" answer pick z
run pick 0 "answered" answer pick B
has picked-lower brand/live/state.json '"picked": "b"'
run recommend 0 "recommend ok" recommend A "The only one that names both halves"
has recommend-kept brand/live/state.json "names both halves"

# a hostile name never reaches the page as markup
printf '\nname: <script>alert(1)</script>\n' >> brand/brief.md
run refresh-hostile 0 "refresh ok" refresh
has name-reached-state brand/live/state.json "alert(1)"
lacks no-raw-script brand/index.html "<script>alert(1)"
has escaped-in-json brand/index.html "\\u003cscript\\u003ealert(1)"

# finish and root
run ask-before-finish 0 "ask ok" ask late --text "Still open?" --suggest yes
run finish 0 "finish ok" finish
lacks finish-closes-open brand/live/state.json '"status": "open"'
has finished brand/live/state.json '"status": "done"'
# a finished brief, or a page on a static host, must not poll /api/state forever
has final-no-poll brand/index.html 'if (served && !done())'
has static-host-stops brand/index.html 'fails >= 3 && !connected) clearInterval(timer)'
cd "$WORK" || exit 1
run root 0 "status\|url" --root proj status
run root-missing 2 "not a directory" --root "$WORK/nope" status

# the server, in process: token, origin, hidden files, traversal
python3 -I - "$SCRIPT" "$WORK/proj" <<'PY'
import importlib.util, json, socket, sys, threading, http.client, http.server
spec = importlib.util.spec_from_file_location("brdlive", sys.argv[1]); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
root = sys.argv[2]
import os; os.chdir(root)
m.mutate(root, lambda st: st["questions"].append({"id": "q9", "text": "Ok?", "suggest": "yes", "options": ["yes", "no"], "kind": "choice", "status": "open", "answer": None, "asked": "x"}))
open(os.path.join(root, "brand", "live", "server.json"), "w").write('{"pid": 1, "port": 1}')
open(os.path.join(root, "brand", "live", ".lock2.lock"), "w").write("x")
s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
tok = "tok123"
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), m.make_handler(root, tok, port))
threading.Thread(target=srv.serve_forever, daemon=True).start()
bad = 0
def chk(name, ok):
    global bad
    print(("ok   " if ok else "FAIL ") + name)
    bad += (not ok)
def req(method, path, body=None, headers=None):
    c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    c.request(method, path, body=body, headers=headers or {})
    r = c.getresponse(); d = r.read(); c.close(); return r.status, d
st, d = req("GET", "/api/state"); chk("state served with token", st == 200 and json.loads(d).get("token") == tok)
st, d = req("GET", "/"); chk("index served at /", st == 200 and b"Brand design brief" in d)
st, d = req("GET", "/live/server.json"); chk("server.json hidden", st == 404)
st, d = req("GET", "/live/.lock2.lock"); chk("lock file hidden", st == 404)
st, d = req("GET", "/../../../../etc/passwd"); chk("no traversal", st != 200 or b"root:" not in d)
st, d = req("GET", "/brand"); chk("no directory listing", st in (301, 404))
j = json.dumps({"id": "q9", "value": "yes"}); h = {"Content-Type": "application/json"}
st, d = req("POST", "/api/answer", j, h); chk("post without token refused", st == 403)
st, d = req("POST", "/api/answer", j, dict(h, **{"X-Brd-Token": "wrong"})); chk("post with wrong token refused", st == 403)
st, d = req("POST", "/api/answer", j, dict(h, **{"X-Brd-Token": tok, "Origin": "http://evil.example"})); chk("post from another origin refused", st == 403)
st, d = req("POST", "/api/answer", json.dumps({"id": "q9", "value": "maybe"}), dict(h, **{"X-Brd-Token": tok})); chk("answer outside the options refused", st == 400)
st, d = req("POST", "/api/answer", "x" * 30000, dict(h, **{"X-Brd-Token": tok})); chk("oversized body refused", st == 400)
st, d = req("POST", "/api/answer", j, dict(h, **{"X-Brd-Token": tok, "Origin": "http://127.0.0.1:%d" % port})); chk("good answer accepted", st == 200)
a = json.load(open(os.path.join(root, "brand", "live", "answers.json"))); chk("answer recorded", a.get("q9", {}).get("value") == "yes")
st, d = req("GET", "/api/state"); chk("state shows the answer", any(q["id"] == "q9" and q["status"] == "answered" for q in json.loads(d)["questions"]))
srv.shutdown()
sys.exit(1 if bad else 0)
PY
rc=$?
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL server checks (see lines above)"; fi

# The page's own script, run under node with a stub DOM: with a pick question open and three concepts,
# the first successful poll must show the Pick buttons even though the state has not changed, and the tab title says it is the user's turn.
if command -v node >/dev/null 2>&1; then
  mkdir -p pickproj/brand && cp "$FIX/brief-roles-good.md" pickproj/brand/brief.md
  for c in a b c; do mkdir -p pickproj/brand/concepts/$c && cp "$FIX/good.svg" pickproj/brand/concepts/$c/concept.svg; done
  (cd pickproj && python3 -I "$SCRIPT" refresh >/dev/null && python3 -I "$SCRIPT" ask pick --kind pick --text "Which concept?" --suggest a --option a --option b --option c >/dev/null)
  node - pickproj/brand/index.html <<'JS'
const fs = require("fs"), vm = require("vm");
const html = fs.readFileSync(process.argv[2], "utf8");
const code = html.slice(html.lastIndexOf("<script>") + 8, html.lastIndexOf("</script>"));
const els = {}, el = s => els[s] || (els[s] = { innerHTML: "", appendChild() {} });
const state = JSON.parse(code.match(/const STATE = (.*);/)[1]);
const ctx = {
  location: { protocol: "http:" }, console,
  document: { querySelector: s => s === "#appFrame" ? null : el(s), querySelectorAll: () => [], addEventListener() {}, activeElement: null, title: "" },
  IntersectionObserver: class { observe() {} disconnect() {} },
  fetch: async () => ({ ok: true, json: async () => Object.assign({}, state, { updated: "later", token: "t" }) }),
  setInterval: fn => { ctx.tick = fn; return 1; }, clearInterval() {}, encodeURIComponent,
};
vm.createContext(ctx); vm.runInContext(code, ctx);
setTimeout(() => {
  const main = el("#main").innerHTML, live = el("#live").innerHTML;
  const ok = (main.match(/data-pick="/g) || []).length === 3 && live.includes("Live") && ctx.document.title.startsWith("\u25CF Your turn");
  if (!ok) console.log("FAIL pick buttons after the first poll: " + (main.match(/data-pick="/g) || []).length + " buttons; status " + live.replace(/<[^>]+>/g, "") + "; title " + ctx.document.title);
  if (!ok) process.exit(1);
  // the user picks b: the next poll shows it as recorded, not the buttons
  const q = state.questions.find(q => q.id === "pick"); q.status = "answered"; q.answer = "b"; state.picked = "b";
  ctx.tick();
  setTimeout(() => {
    const m2 = el("#main").innerHTML;
    const ok2 = m2.includes("Recorded") && m2.includes("concept B") && m2.includes("your change") && !m2.includes('data-pick="');
    if (!ok2) console.log("FAIL a recorded answer must show as Recorded, with no Pick buttons left");
    process.exit(ok2 ? 0 : 1);
  }, 50);
}, 50);
JS
  if [ $? -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi
else
  echo "skip pick buttons after the first poll: node not installed"
fi

echo "brdlive tests: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
