#!/usr/bin/env python3
"""brdlive: the live page of a /brand-create run (see SPEC.md).

One browser tab shows the run as it happens (progress, questions, concepts, kit) and, at the end, is the brand analysis report.
The page is brand/index.html; its state is brand/live/state.json. The server listens on 127.0.0.1 only and serves the brand folder.
Python standard library only. Exit codes: 0 done, 2 usage or input error, 3 wait timed out.
"""
import argparse, fcntl, glob, html, http.server, json, os, re, secrets, signal, socket, sys, tempfile, threading, time, urllib.parse, webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brdcheck  # noqa: E402  (same folder; -I removes the script dir from sys.path)

VERSION = "0.1.0"
TEMPLATE = os.path.join(HERE, "..", "..", "..", "templates", "live-page.html")
STEPS = [("brief", "Brief"), ("shortlist", "Shortlist"), ("concepts", "Three concepts"), ("review", "Blind review"),
         ("pick", "Your pick"), ("kit", "Kit: palette, wordmark, lockups"), ("story", "Story and brand sheet"),
         ("export", "Exports and applications page"), ("final", "Final review")]
STATUSES = ("pending", "active", "done", "skipped")
MAX_BODY = 20000
ROLE = {"mark": "Master mark, flat colours", "mark-mono": "One colour", "mark-reversed": "For dark backgrounds",
        "mark-reversed-tile": "Reversed mark on a dark tile (preview)", "mark-gradient": "Gradient version",
        "wordmark": "Outlined name", "wordmark-reversed": "Outlined name, dark backgrounds",
        "lockup-horizontal": "Mark and name side by side", "lockup-horizontal-reversed": "Side by side, dark backgrounds",
        "lockup-stacked": "Mark above name", "lockup-stacked-reversed": "Mark above name, dark backgrounds"}
FOLDER = [("index.html", "This page: the live view while the run lasts, the report afterwards"),
          ("brief.md", "The brief: narrative, declaration, shortlist, palette roles, rationale, story"),
          ("brand-sheet.md", "The brand sheet: story, positioning, palette, type, clear space, legal notes"),
          ("review.md", "The latest review verdict, with the earlier concept review below it"),
          ("*.svg", "The logo files: master mark, variants, wordmark and lockups (SVG, outlined, no live text)"),
          ("wordmark.json", "Record of the font and the outlining step"),
          ("applications.html", "The kit placed in everyday applications, every colour pair measured"),
          ("concepts/", "The three greyscale concepts, each with its notes and renders"),
          ("exports/", "The downloadable set: svg/, png/ (transparent), manifest.json and the zip"),
          ("renders/", "PNG renders the checks looked at"), ("checks/", "JSON output of brdcheck"),
          ("live/", "State of this page; safe to delete once the run is over")]


class Fail(Exception):
    pass


# ---- files and locking -----------------------------------------------------
def paths(root):
    brand = os.path.join(root, "brand")
    live = os.path.join(brand, "live")
    return brand, live


def atomic(path, text):
    d = os.path.dirname(path)
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".tmp-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


class Lock:
    def __init__(self, live):
        os.makedirs(live, exist_ok=True)
        self.f = open(os.path.join(live, ".lock"), "w")

    def __enter__(self):
        fcntl.flock(self.f, fcntl.LOCK_EX)

    def __exit__(self, *a):
        fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def base_state():
    return {"steps": [{"id": i, "title": t, "status": "pending", "note": ""} for i, t in STEPS], "questions": [],
            "recommendation": None, "picked": None, "run": {"status": "running", "started": now(), "finished": None}}


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return ""


# ---- scanning the brand folder ----------------------------------------------
def declared(text, key):
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else ""


def section(text, title):
    m = re.search(r"^#{1,6}[ \t]+%s[ \t]*$(.*?)(?=^#{1,6}[ \t]|\Z)" % re.escape(title), text, re.M | re.S | re.I)
    return re.sub(r"<!--.*?-->", "", m.group(1), flags=re.S).strip() if m else ""


def shortlist(text):
    rows = []
    for line in section(text, "Shortlist").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0].isdigit():
            rows.append({"n": int(cells[0]), "line": cells[1], "kind": cells[2], "score": cells[3], "chosen": cells[4]})
    return rows


def scan(root, st):
    brand, _ = paths(root)
    brief_path = os.path.join(brand, "brief.md")
    text = read(brief_path)
    out = {"name": declared(text, "name") or None}
    out["brief"] = None
    if text:
        try:
            b = brdcheck.read_brief(brief_path)
        except brdcheck.InputError:
            b = None
        if b:
            keys = ("concept", "audience", "tone", "avoid", "metaphor", "positioning", "own-word", "assets", "category-colours",
                    "scope", "wordmark-font", "story-status", "pair-cue")
            out["brief"] = {k: declared(text, k) for k in keys}
            out["brief"].update(narrative=section(text, "Narrative"), story=b["story"], rationale=b["rationale"],
                                shortlist=shortlist(text), assumed=(re.search(r"^Assumed.*$", text, re.M) or [""])[0])
            roles = []
            for r in b["roles"]:
                row = dict(r)
                if r["light"] and r["dark"]:
                    bgl = next((x["light"] for x in b["roles"] if x["role"] == "background"), None)
                    bgd = next((x["dark"] for x in b["roles"] if x["role"] == "background"), None)
                    if bgl and bgd and r["role"] != "background":
                        row["cl"], row["cd"] = round(brdcheck.contrast(r["light"], bgl), 2), round(brdcheck.contrast(r["dark"], bgd), 2)
                roles.append(row)
            out["brief"]["roles"] = roles
    # concepts
    chosen = {}
    for r in (out["brief"] or {}).get("shortlist", []):
        m = re.search(r"\(([A-C])\)", r["chosen"])
        if m:
            chosen[m.group(1).lower()] = r["line"]
    concepts = []
    for c in "abc":
        d = os.path.join(brand, "concepts", c)
        if os.path.isfile(os.path.join(d, "concept.svg")):
            notes = read(os.path.join(d, "notes.md"))
            m = re.search(r"^Concept:\s*(.*)$", notes, re.M)
            rend = {k: "concepts/%s/renders/concept-%s.png" % (c, k) for k in ("16", "64", "display", "mono", "reversed")
                    if os.path.isfile(os.path.join(d, "renders", "concept-%s.png" % k))}
            concepts.append({"id": c, "line": chosen.get(c) or (m.group(1) if m else ""), "svg": "concepts/%s/concept.svg" % c, "renders": rend})
    out["concepts"] = concepts
    picked = st.get("picked")
    if not picked:
        m = re.search(r"Chosen concept:\s*([A-C])\b", read(os.path.join(brand, "brand-sheet.md")))
        picked = m.group(1).lower() if m else None
    out["picked"] = picked.lower() if picked else None
    # logo files
    logo = []
    for p in sorted(glob.glob(os.path.join(brand, "*.svg"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        logo.append({"file": stem + ".svg", "role": ROLE.get(stem, "Extra"), "dark": bool(re.search(r"(^|[-_.])(reversed|dark)([-_.]|$)", stem)),
                     "tile": bool(re.search(r"tile", stem))})
    out["logo"] = sorted(logo, key=lambda x: (x["file"] != "mark.svg", x["file"]))
    # exports, checks, docs
    man = load_json(os.path.join(brand, "exports", "manifest.json"), None)
    zips = sorted(glob.glob(os.path.join(brand, "exports", "*.zip")))
    out["exports"] = {"files": len(man["files"]), "sizes": man.get("sizes", []), "zip": "exports/" + os.path.basename(zips[0]) if zips else None} if man else None
    chk = load_json(os.path.join(brand, "checks", "check.json"), {})
    out["checks"] = chk.get("summary")
    out["review"] = read(os.path.join(brand, "review.md"))
    sheet = read(os.path.join(brand, "brand-sheet.md"))
    out["sheet"] = sheet
    m = re.search(r"^## Legal notes.*?(?=^## |\Z)", sheet, re.M | re.S)
    out["legal"] = m.group(0).strip() if m else ""
    m = re.search(r"^Verdict:\s*([^.\n(`]*)", out["review"], re.M)  # the phrase, not the sentence after it
    out["verdict"] = m.group(1).strip() if m and m.group(1).strip() else None
    out["applications"] = os.path.isfile(os.path.join(brand, "applications.html"))
    out["folder"] = [{"path": p, "what": d, "exists": bool(glob.glob(os.path.join(brand, p.rstrip("/"))))} for p, d in FOLDER]
    return out


# ---- state and page ---------------------------------------------------------
def state_path(root):
    return os.path.join(paths(root)[1], "state.json")


def refresh(root):
    """Rebuild state.json and index.html from the live state plus a scan of the folder. Caller holds the lock."""
    brand, live = paths(root)
    st = load_json(state_path(root), None) or base_state()
    full = dict(st)
    full.update(scan(root, st))
    full["updated"] = now()
    full["version"] = VERSION
    atomic(state_path(root), json.dumps(full, indent=1))
    tpl = read(TEMPLATE)
    if not tpl:
        raise Fail("cannot read the page template: %s" % os.path.normpath(TEMPLATE))
    blob = json.dumps(full).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    atomic(os.path.join(brand, "index.html"), tpl.replace("/*__STATE__*/null", blob, 1))
    return full


def mutate(root, fn):
    brand, live = paths(root)
    os.makedirs(live, exist_ok=True)
    with Lock(live):
        st = load_json(state_path(root), None) or base_state()
        fn(st)
        atomic(state_path(root), json.dumps(st, indent=1))
        return refresh(root)


def set_step(st, sid, status, note=""):
    s = next((x for x in st["steps"] if x["id"] == sid), None)
    if not s:
        raise Fail("unknown step %r; steps are: %s" % (sid, ", ".join(i for i, _ in STEPS)))
    if status not in STATUSES:
        raise Fail("status must be one of: " + ", ".join(STATUSES))
    s["status"] = status
    if note:
        s["note"] = note
    if status in ("done", "skipped"):
        advance(st)


def advance(st):
    """With no step in progress, start the next pending one, so the page never sits idle between steps."""
    if any(x["status"] == "active" for x in st["steps"]):
        return
    nxt = next((x for x in st["steps"] if x["status"] == "pending"), None)
    if nxt and st.get("run", {}).get("status") != "done":
        nxt["status"] = "active"


def say(st, text):
    """Post a progress message on the step in progress (the latest one started), so the page tells what the terminal tells."""
    advance(st)
    act = [x for x in st["steps"] if x["status"] == "active"]
    if not act:
        raise Fail("no step in progress to say this on; start one with: step <id> active")
    act[-1]["note"] = str(text)[:400]


def record_answer(root, qid, value):
    """Store an answer in answers.json and on the question. Caller must not hold the lock."""
    brand, live = paths(root)
    value = str(value)[:2000]
    with Lock(live):
        st = load_json(state_path(root), None) or base_state()
        q = next((x for x in st["questions"] if x["id"] == qid), None)
        if not q:
            raise Fail("no question %r" % qid)
        if q["status"] == "answered":
            raise Fail("question %r is already answered" % qid)
        if q.get("options") and q.get("kind") != "text":
            match = next((o for o in q["options"] if o.casefold() == value.strip().casefold()), None)
            if match is None:
                raise Fail("answer must be one of: " + ", ".join(q["options"]))
            value = match
        q.update(status="answered", answer=value, answered=now())
        if qid == "pick":
            st["picked"] = value.lower()
            set_step(st, "pick", "done")
        ans = load_json(os.path.join(live, "answers.json"), {})
        ans[qid] = {"value": value, "at": q["answered"]}
        atomic(os.path.join(live, "answers.json"), json.dumps(ans, indent=1))
        atomic(state_path(root), json.dumps(st, indent=1))
        refresh(root)
    return q


# ---- server -----------------------------------------------------------------
def make_handler(root, token, port):
    brand, live = paths(root)
    allowed = {"http://127.0.0.1:%d" % port, "http://localhost:%d" % port}

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=brand, **k)

        def log_message(self, *a):
            pass

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def list_directory(self, path):
            self.send_error(404)

        def json(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            p = urllib.parse.urlparse(self.path).path
            if p == "/api/state":
                st = load_json(state_path(root), {})
                st["token"] = token
                return self.json(200, st)
            if p == "/live/server.json" or p.endswith(".lock") or "/.tmp-" in p:  # server.json and temp files stay private
                return self.send_error(404)
            return super().do_GET()

        def do_POST(self):
            p = urllib.parse.urlparse(self.path).path
            origin = self.headers.get("Origin")
            if p != "/api/answer" or (origin and origin not in allowed) or self.headers.get("X-Brd-Token") != token:
                return self.json(403, {"error": "refused"})
            try:
                n = int(self.headers.get("Content-Length", "0"))
                if not 0 < n <= MAX_BODY:
                    raise ValueError
                body = json.loads(self.rfile.read(n))
                q = record_answer(root, str(body["id"]), body["value"])
            except Fail as e:
                return self.json(400, {"error": str(e)})
            except (ValueError, KeyError, TypeError):
                return self.json(400, {"error": "bad request"})
            return self.json(200, {"ok": True, "id": q["id"]})

    return H


def alive(info):
    try:
        os.kill(info["pid"], 0)
        with socket.create_connection(("127.0.0.1", info["port"]), timeout=1):
            return True
    except (OSError, KeyError, TypeError):
        return False


def serve(root, port, open_browser):
    brand, live = paths(root)
    os.makedirs(live, exist_ok=True)
    info_path = os.path.join(live, "server.json")
    info = load_json(info_path, None)
    if alive(info):
        print("brdlive: already running at http://127.0.0.1:%d/" % info["port"])
        return 0
    with Lock(live):
        if not os.path.isfile(state_path(root)):
            st = base_state()
            st["steps"][0]["status"] = "active"  # the page shows work from the first second
            atomic(state_path(root), json.dumps(st, indent=1))
        refresh(root)
    token = secrets.token_urlsafe(24)
    srv = None
    for p in range(port, port + 30):
        try:
            handler = make_handler(root, token, p)
            srv = http.server.ThreadingHTTPServer(("127.0.0.1", p), handler)
            break
        except OSError:
            continue
    if not srv:
        raise Fail("no free port from %d to %d" % (port, port + 29))
    port = srv.server_address[1]
    atomic(info_path, json.dumps({"pid": os.getpid(), "port": port}))
    url = "http://127.0.0.1:%d/" % port
    print("brdlive: serving %s at %s (stop with: brdlive.py stop)" % (os.path.relpath(brand), url), flush=True)
    if open_browser:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()

    def bye(*a):
        threading.Thread(target=srv.shutdown, daemon=True).start()
    signal.signal(signal.SIGTERM, bye)
    signal.signal(signal.SIGINT, bye)
    try:
        srv.serve_forever()
    finally:
        try:
            os.remove(info_path)
        except OSError:
            pass
        srv.server_close()
    return 0


# ---- commands ---------------------------------------------------------------
def cmd_wait(root, qid, timeout):
    brand, live = paths(root)
    end = time.time() + timeout
    while time.time() < end:
        a = load_json(os.path.join(live, "answers.json"), {}).get(qid)
        if a:
            print(json.dumps({"id": qid, "answer": a["value"]}))
            return 0
        time.sleep(1)
    print("brdlive: no answer to %r after %d s; the question stays open on the page" % (qid, timeout))
    return 3


def main(argv=None):
    ap = argparse.ArgumentParser(prog="brdlive", description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None, help="project folder that holds brand/ (default: the current directory)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start", help="create the page and serve it (run in the background); opens the browser")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--no-open", action="store_true")
    s = sub.add_parser("step", help="set a step's status")
    s.add_argument("id"); s.add_argument("status", choices=STATUSES); s.add_argument("--note", default="")
    s = sub.add_parser("say", help="post a progress message on the step in progress (say on the page what you tell the user)")
    s.add_argument("text")
    s = sub.add_parser("ask", help="put a question on the page")
    s.add_argument("id"); s.add_argument("--text", required=True); s.add_argument("--suggest", required=True, help="the suggested answer")
    s.add_argument("--option", action="append", default=[], help="a fixed choice; repeat for more")
    s.add_argument("--kind", choices=("choice", "text", "pick"), default=None)
    s = sub.add_parser("wait", help="block until a question is answered; prints the answer as JSON")
    s.add_argument("id"); s.add_argument("--timeout", type=int, default=540)
    s = sub.add_parser("answer", help="answer a question from the terminal")
    s.add_argument("id"); s.add_argument("value")
    s = sub.add_parser("recommend", help="mark the recommended concept on the page")
    s.add_argument("concept", choices=("a", "b", "c", "A", "B", "C")); s.add_argument("reason")
    sub.add_parser("refresh", help="rebuild state.json and index.html from the folder")
    sub.add_parser("finish", help="mark the run done: the page becomes the report")
    sub.add_parser("stop", help="stop the server")
    sub.add_parser("status", help="print the URL and the open questions")
    a = ap.parse_args(argv)
    try:
        if a.root:
            if not os.path.isdir(a.root):
                raise Fail("--root is not a directory: %s" % a.root)
            os.chdir(a.root)
        root = os.getcwd()
        brand, live = paths(root)
        if a.cmd == "start":
            return serve(root, a.port, not a.no_open)
        if a.cmd == "wait":
            return cmd_wait(root, a.id, a.timeout)
        if a.cmd == "answer":
            record_answer(root, a.id, a.value)
            print("brdlive: answered %s" % a.id)
            return 0
        if a.cmd == "stop":
            info = load_json(os.path.join(live, "server.json"), None)
            if not alive(info):
                print("brdlive: no server running")
                return 0
            os.kill(info["pid"], signal.SIGTERM)
            print("brdlive: stopped")
            return 0
        if a.cmd == "status":
            info = load_json(os.path.join(live, "server.json"), None)
            print("url: " + ("http://127.0.0.1:%d/" % info["port"] if alive(info) else "not serving (open brand/index.html as a snapshot)"))
            for q in (load_json(state_path(root), {}).get("questions") or []):
                print("%s: %s%s" % (q["id"], q["status"], " = " + q["answer"] if q.get("answer") else ""))
            return 0

        def apply(st):
            if a.cmd == "step":
                set_step(st, a.id, a.status, a.note)
            elif a.cmd == "say":
                say(st, a.text)
            elif a.cmd == "ask":
                kind = a.kind or ("choice" if a.option else "text")
                if any(q["id"] == a.id for q in st["questions"]):
                    raise Fail("question %r already exists" % a.id)
                st["questions"].append({"id": a.id, "text": a.text, "suggest": a.suggest, "options": a.option, "kind": kind,
                                        "status": "open", "answer": None, "asked": now()})
                if a.id == "pick":
                    set_step(st, "pick", "active")
            elif a.cmd == "recommend":
                st["recommendation"] = {"concept": a.concept.lower(), "reason": a.reason}
            elif a.cmd == "finish":
                st["run"].update(status="done", finished=now())
                for q in st["questions"]:  # a final brief shows no live answer form
                    if q["status"] == "open":
                        q["status"] = "closed"
                for x in st["steps"]:
                    if x["status"] in ("pending", "active"):
                        x["status"] = "done"
        mutate(root, apply)
        print("brdlive: %s ok" % a.cmd)
        if a.cmd == "ask":  # the same question for the terminal: ask in both places, answer in either
            print("Ask in the terminal too: %s Suggested: %s.%s Answer here or on the page." %
                  (a.text, a.suggest, (" Options: " + ", ".join(a.option) + ".") if a.option else ""))
        return 0
    except (Fail, brdcheck.InputError) as ex:
        print("brdlive: %s" % ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
